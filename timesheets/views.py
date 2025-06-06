from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from .models import Timesheet, Period, STATUS, Activity
from staff.models import Staff
from .serializers import TimesheetSerializer, PeriodSerializer, ActivitySerializer, TimesheetReportSerializer, DistrictSerializer
import datetime
from staff.models import Staff, District
from django.db.models import Q
from django.contrib.auth.models import User
from decimal import Decimal
from rest_framework import generics
from .tasks import send_hr_approval_notification, send_submitter_notification
from staff.models import Staff


class ApproveDetailApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get_object(self, timesheet_id, user_id):
        '''
        Helper method to get the object with given timesheet_id, and user_id
        '''

        staff = Staff.objects.get(user=user_id)

        if staff.hr_approval:
            try:
                return Timesheet.objects.get(id=timesheet_id)
            except Timesheet.DoesNotExist:
                return None

        try:
            return Timesheet.objects.get(id=timesheet_id, line_manager=user_id)
        except Timesheet.DoesNotExist:
            return None

    # Approve the timesheet
    def put(self, request, timesheet_id, action=None, *args, **kwargs):
        '''
        Do the timesheet approvals this can be first approval or second approval
        '''
        staff = Staff.objects.get(user=request.user.id)

        timesheet_instance = self.get_object(timesheet_id, request.user.id)
        if not timesheet_instance:
            return Response(
                {"res": "Object with timesheet id does not exists or you do not have the rights"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # initialize the data object
        data = {}
        # Get the current actions list (or initialize as empty list if None)
        current_actions = timesheet_instance.actions or []

        if action == 'approve':
            # if the current status is SUBMITTED, then set the first_approver, date and status
            if timesheet_instance.current_status == Timesheet.Current_Status.SUBMITTED:
                if request.user.id == timesheet_instance.line_manager.id:
                    data['first_approval_date'] = datetime.datetime.now()
                    data['first_approver'] = request.user.id
                    data['current_status'] = Timesheet.Current_Status.LINE_APPROVED
                    current_actions.append({
                        "action": "line_manager_approval",
                        "responsible": f"{request.user.first_name} {request.user.last_name}",
                        "date": datetime.datetime.now().strftime("%Y-%m-%d")
                    })
                    data['actions'] = current_actions
                else:
                    return Response(f'In order to complete a line manager approval user has to be line manager of the staff, for this timesheet the line manager is {timesheet_instance.created_by.email}', status=status.HTTP_400_BAD_REQUEST)
            elif timesheet_instance.current_status == Timesheet.Current_Status.LINE_APPROVED:
                if staff.hr_approval:
                    data['second_approver'] = request.user.id
                    data['second_approval_date'] = datetime.datetime.now()
                    # Append HR approval to actions
                    data['current_status'] = Timesheet.Current_Status.HR_APPROVED
                    current_actions.append({
                        "action": "hr_approval",
                        "responsible": f"{request.user.first_name} {request.user.last_name}",
                        "date": datetime.datetime.now().strftime("%Y-%m-%d")
                    })
                    data['actions'] = current_actions
                else:
                    return Response(f'In order to complete an HR approval user has to be in HR Dept current user departnment is {staff.department.name}', status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(f'Cannot approve a timesheet that has the current status {timesheet_instance.current_status}. Current status has to be submitted or line approved', status=status.HTTP_400_BAD_REQUEST)

        elif action == 'reject':
            # Rejection logic
            if timesheet_instance.current_status in [Timesheet.Current_Status.SUBMITTED, Timesheet.Current_Status.LINE_APPROVED]:
                # Check if rejection reason is provided in the request data
                rejection_reason = request.data.get("rejection_reason")
                if not rejection_reason:
                    return Response(
                        {"res": "Rejection reason is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update timesheet with rejection details
                data["current_status"] = Timesheet.Current_Status.REJECTED
                data["comment"] = rejection_reason
                # Optional: track who rejected it
                data["rejected_by"] = request.user.id
                # Optional: track when it was rejected
                data["rejected_date"] = datetime.datetime.now()
                # Append rejection to actions
                action_type = ("line_manager_rejection" if timesheet_instance.current_status == Timesheet.Current_Status.SUBMITTED
                               else "hr_rejection")
                current_actions.append({
                    "action": action_type,
                    "responsible": f"{request.user.first_name} {request.user.last_name}",
                    "date": datetime.datetime.now().strftime("%Y-%m-%d")
                })
                data['actions'] = current_actions
            else:
                return Response(
                    f"Cannot reject a timesheet with status {timesheet_instance.current_status}. It must be SUBMITTED or LINE_APPROVED",
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"res": "Invalid action specified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TimesheetSerializer(
            instance=timesheet_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Send notifications based on action and status
            timesheet_data = {
                "id": timesheet_instance.id,
                "submission_date": timesheet_instance.created_at.strftime("%Y-%m-%d"),
                "period": timesheet_instance.period,
                "hours_worked": str(timesheet_instance.total_hours),
                "leave_days": timesheet_instance.leave_days,
                "comment": timesheet_instance.comment or ""
            }
            if action == 'approve' and data['current_status'] == Timesheet.Current_Status.LINE_APPROVED:
                # Notify HR for second approval

                hr_users = User.objects.filter(staff_profile__hr_approval=True)
                for hr_user in hr_users:
                    try:
                        send_hr_approval_notification.delay(
                            hr_email=hr_user.email,
                            hr_name=f"{hr_user.first_name} {hr_user.last_name}",
                            staff_name=f"{timesheet_instance.created_by.first_name} {timesheet_instance.created_by.last_name}",
                            timesheet_data=timesheet_data
                        )
                    except Exception as e:
                        print(
                            f"Failed to send HR notification to {hr_user.email}: {e}")
            elif action == 'approve' and data['current_status'] == Timesheet.Current_Status.HR_APPROVED:
                # Notify submitter of final approval
                send_submitter_notification.delay(
                    submitter_email=timesheet_instance.created_by.email,
                    submitter_name=f"{timesheet_instance.created_by.first_name} {timesheet_instance.created_by.last_name}",
                    timesheet_data=timesheet_data,
                    status="approved"
                )
            elif action == 'reject':
                # Notify submitter of rejection
                send_submitter_notification.delay(
                    submitter_email=timesheet_instance.created_by.email,
                    submitter_name=f"{timesheet_instance.created_by.first_name} {timesheet_instance.created_by.last_name}",
                    timesheet_data=timesheet_data,
                    status="rejected",
                    rejected_by=f"{request.user.first_name} {request.user.last_name}"
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the timesheet items for given requested user
        '''
        staff = Staff.objects.get(user_id=request.user.id)

        # User is first approver and status is submitted
        timesheets = Timesheet.objects.filter(
            line_manager=request.user,
            current_status=Timesheet.Current_Status.SUBMITTED
        )

        # If staff has hr_approval, also show line manager approved
        if staff.hr_approval:
            timesheets |= Timesheet.objects.filter(
                current_status=Timesheet.Current_Status.LINE_APPROVED
            )

        serializer = TimesheetSerializer(timesheets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TimesheetListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the timesheet items for given requested user
        '''
        timesheets = Timesheet.objects.filter(created_by=request.user.id)

        serializer = TimesheetSerializer(timesheets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.data.get('created_by')
        period = request.data.get('period')

       # checking if there is user with same key and period
        existing_timesheet = Timesheet.objects.filter(
            period=period, created_by=user).first()
        line_manager = Staff.objects.get(
            user__id=request.data.get("created_by")).line_manager.pk
        data = {
            'period': request.data.get('period'),
            'projects': request.data.get('completed'),
            'total_hours': request.data.get('total_hours'),
            'leave_days': request.data.get('leave_days'),
            'working_days': request.data.get('working_days'),
            'filled_timesheet': request.data.get('filled_timesheet'),
            'created_at': datetime.datetime.now(),
            'current_status': Timesheet.Current_Status.SUBMITTED,
            'created_by': user,
            'status': STATUS[0][0],
            'line_manager': line_manager
        }

        if existing_timesheet:
            serializer = TimesheetSerializer(
                existing_timesheet, data=data, partial=True)
        else:
            serializer = TimesheetSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if not existing_timesheet else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimesheetDetailApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.AllowAny]

    def get_object(self, timesheet_id, user_id):
        '''
        Helper method to get the object with given timesheet_id, and user_id
        '''
        try:
            return Timesheet.objects.get(id=timesheet_id)
        except Timesheet.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, timesheet_id, *args, **kwargs):
        '''
        Retrieves the Timesheet with given timesheet_id
        '''
        timesheet_instance = self.get_object(timesheet_id, request.user.id)
        if not timesheet_instance:
            return Response(
                {"res": "Object with timesheet id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TimesheetSerializer(timesheet_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    def put(self, request, timesheet_id, *args, **kwargs):
        '''
        Updates the timesheet item with given timesheet_id if exists
        '''
        timesheet_instance = self.get_object(timesheet_id, request.user.id)
        if not timesheet_instance:
            return Response(
                {"res": "Object with timesheet id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {}
        for field in ["period", "current_status", "first_approver", "first_approval_date", "second_approver", "second_approval_date",
                      "rejected_by", "rejected_date", "comment", "total_hours", "leave_days", "working_days", "filled_timesheet", "created_at", "created_by", "status", "edited_at"]:
            if field in request.data:
                data[field] = request.data[field]
        data['user'] = request.user.id
        data['edited_at'] = datetime.datetime.now()

        serializer = TimesheetSerializer(
            instance=timesheet_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, timesheet_id, *args, **kwargs):
        '''
        Deletes the timesheet item with given timesheet_id if exists
        '''
        timesheet_instance = self.get_object(timesheet_id, request.user.id)
        if not timesheet_instance:
            return Response(
                {"res": "Object with timesheet id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        timesheet_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )


class PeriodListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the periods items for given requested user
        '''
        periods = Period.objects.all()
        serializer = PeriodSerializer(periods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeePeriodListApiView(APIView):

    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def generate_timesheet_json(self, period_id, staff_id):
        try:
            # Retrieve the period and staff objects
            period = Period.objects.get(id=period_id)
            staff = Staff.objects.get(id=staff_id)

            # Generate the list of dates within the period
            start_date = period.start_date
            end_date = period.end_date
            dates = [start_date + datetime.timedelta(days=x)
                     for x in range((end_date - start_date).days + 1)]

            # Retrieve the project names associated with the staff member
            project_names = staff.projects.values_list('name', flat=True)

            # Initialize the timesheet dictionary
            timesheet = {}

            # Loop through each date in the period and construct the timesheet entries
            for i, date in enumerate(dates, start=1):
                timesheet_entry = {
                    'date': date.strftime('%Y-%m-%d'),
                    'projects': {project: 0 for project in project_names},
                    'leave': {
                        'sick_leave': 0,
                        'study_leave': 0,
                        'maternity_paternity_leave': 0,
                        'compassionate_leave': 0,
                        'unpaid_leave': 0,
                        'administrative_leave': 0,
                        'public_leave': 0,
                        'annual_leave': 0,
                    },
                }
                timesheet[i] = timesheet_entry

            return timesheet

        except Period.DoesNotExist:
            return JsonResponse({'error': 'Period not found'}, status=404)
        except Staff.DoesNotExist:
            return JsonResponse({'error': 'Staff not found'}, status=404)

    # 1. List all
    def get(self, request, period_id, *args, **kwargs):
        '''
        List all the periods items for given requested user
        '''
        timesheet = Timesheet.objects.filter(
            period=period_id, created_by=request.user)

        if timesheet.exists():
            serializer = TimesheetSerializer(timesheet)
        else:
            serializer = self.generate_timesheet_json(
                period_id, request.user.id)

        return Response(serializer, status=status.HTTP_200_OK)


class ActivityListApiView(APIView):
    def get(self, request, *args, **kwargs):
        activities = Activity.objects.all()
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data,  status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# activity api class
class ActivityDetailApiView(APIView):
    def get_object(self, activity_id):
        try:
            return Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return None

    def get(self, request, activity_id):
        activity_instance = self.get_object(activity_id)
        if not activity_instance:
            return Response({"res": "Object with activity id does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ActivitySerializer(activity_instance)
        return Response(serializer.data)

    def put(self, request, activity_id):
        activity_instance = self.get_object(activity_id)
        if not activity_instance:
            return Response({"res": "Object with activity id does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ActivitySerializer(
            instance=activity_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, activity_id):
        activity_instance = self.get_object(activity_id)
        if not activity_instance:
            return Response({"res": "Object with activity id does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        activity_instance.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)


# api class for getting all districts
class DistrictView(generics.ListAPIView):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class TimesheetReportView(APIView):
    def get(self, request):
        timesheets = Timesheet.objects.filter(
            current_status=Timesheet.Current_Status.HR_APPROVED)
        report_data = []
        for timesheet in timesheets:
            if timesheet.filled_timesheet is not None and isinstance(timesheet.filled_timesheet, dict):
                userid = timesheet.created_by_id
                staffdetails = Staff.objects.get(user=userid)
                employeeid = staffdetails.employee_number
                district = staffdetails.district
                period = timesheet.period
                namedetails = User.objects.get(id=userid)
                fullname = namedetails.first_name + " " + namedetails.last_name
                department = staffdetails.department
                projects = {}
                total_project_hours = 0

                for day, data in timesheet.filled_timesheet.items():
                    if isinstance(data, dict):
                        for project, hours in data.get('projects', {}).items():
                            if project not in projects:
                                projects[project] = {'hours': 0}
                            if hours:
                                projects[project]['hours'] += float(hours)
                                total_project_hours += float(hours)

                total_hours = timesheet.total_hours
                total_leave_hours = total_hours - Decimal(total_project_hours)

                loe = ((Decimal(total_project_hours) / Decimal(total_hours))
                       * 100).quantize(Decimal('0.01'))

                for project, project_data in projects.items():
                    project_loe = ((Decimal(
                        project_data['hours']) / Decimal(total_hours)) * 100).quantize(Decimal('0.01'))
                    projects[project]['loe'] = project_loe

                report_entry = {
                    "id": timesheet.pk,
                    'employee_id': employeeid,
                    'staff_name': fullname,
                    'district': district,
                    'project': projects,
                    'total_hours': total_hours,
                    'total_work_hours': total_project_hours,
                    'total_leave_hours': total_leave_hours,
                    'total_available_hours': total_hours,
                    'LOE': loe,
                    "period": period,
                    "department": department
                }
                report_data.append(report_entry)
        serializer = TimesheetReportSerializer(report_data, many=True)
        return Response(serializer.data)
