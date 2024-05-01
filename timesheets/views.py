from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Timesheet, STATUS
from .serializers import TimesheetSerializer
import datetime
from staff.models import Staff
from django.db.models import Q
from django.contrib.auth.models import User


class ApproveDetailApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, timesheet_id, user_id):
        '''
        Helper method to get the object with given timesheet_id, and user_id
        '''

        staff = Staff.objects.get(user=user_id)

        if staff.department.id == 2:
            try:
                return Timesheet.objects.get(id=timesheet_id)
            except Timesheet.DoesNotExist:
                return None

        try:
            return Timesheet.objects.get(id=timesheet_id, first_approver=user_id)
        except Timesheet.DoesNotExist:
            return None

    # Approve the timesheet
    def put(self, request, timesheet_id, *args, **kwargs):
        '''
        Do the timesheet approvals this can be first approval or second approval
        '''
        staff = Staff.objects.get(user=request.user.id)

        timesheet_instance = self.get_object(timesheet_id, request.user.id)
        if not timesheet_instance:
            return Response(
                {"res": "Object with timesheet id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # initialize the data object
        data = {}
        # if the current status is SUBMITTED, then set the first_approver and f
        if timesheet_instance.current_status == Timesheet.Current_Status.SUBMITTED:
            if request.user.id == timesheet_instance.first_approver.id:
                data['first_approval_date'] = datetime.datetime.now()
                data['current_status'] = Timesheet.Current_Status.LINE_APPROVED
            else:
                return Response(f'In order to complete a line manager approval user has to be line manager of the staff, for this timesheet the line manager is {timesheet_instance.created_by.email}', status=status.HTTP_400_BAD_REQUEST)
        elif timesheet_instance.current_status == Timesheet.Current_Status.LINE_APPROVED:
            if staff.department.id == 2:
                data['second_approver'] = request.user.id
                data['second_approval_date'] = datetime.datetime.now()
                data['current_status'] = Timesheet.Current_Status.HR_APPROVED
            else:
                return Response(f'In order to complete an HR approval user has to be in HR Dept current user departnment is {staff.department.name}', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(f'Cannot approve a timesheet that has the current status {timesheet_instance.current_status}. Current status has to be submitted or line approved', status=status.HTTP_400_BAD_REQUEST)

        serializer = TimesheetSerializer(
            instance=timesheet_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        staff = Staff.objects.get(user_id=request.user.id)

        '''
        List all the timesheet items for given requested user
        '''

        if staff.department.id == 2:
            timesheets = Timesheet.objects.filter(
                Q(first_approver=request.user.id) &
                Q(current_status=Timesheet.Current_Status.SUBMITTED)) | Timesheet.objects.filter(
                current_status=Timesheet.Current_Status.LINE_APPROVED)

        else:
            timesheets = Timesheet.objects.filter(
                first_approver=request.user.id, current_status=Timesheet.Current_Status.SUBMITTED)

        serializer = TimesheetSerializer(timesheets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TimesheetListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the timesheet items for given requested user
        '''
        timesheets = Timesheet.objects.filter(created_by=request.user.id)
        serializer = TimesheetSerializer(timesheets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Timesheet with given timesheet data
        '''
        staff = Staff.objects.get(user_id=request.user.id)

        data = {
            'period': request.data.get('period'),
            'projects': request.data.get('completed'),
            'total_hours': request.data.get('total_hours'),
            'leave_days': request.data.get('leave_days'),
            'working_days': request.data.get('working_days'),
            'filled_timesheet': request.data.get('filled_timesheet'),
            'first_approver': staff.line_manager.id,
            'created_at': datetime.datetime.now(),
            'current_status': Timesheet.Current_Status.SUBMITTED,
            'created_by': request.user.id,
            'status': STATUS[0][0],

        }
        serializer = TimesheetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimesheetDetailApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

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

        # data = {
        #     'task': request.data.get('task'),
        #     'completed': request.data.get('completed'),
        #     'user': request.user.id
        # }

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
