from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsApplicantOrAdmin
from .models import ClientRequest, Course, LessonBalance, Payment
from .applicant_serializers import (
    ApplicantBalanceSerializer,
    ApplicantClientRequestCreateSerializer,
    ApplicantCourseSerializer,
    ApplicantPaymentSerializer,
)


class PublicCoursesListAPI(generics.ListAPIView):
    """
    Public list of courses for the landing page.
    GET /api/applicant/courses/public/
    """

    permission_classes = [AllowAny]
    serializer_class = ApplicantCourseSerializer

    def get_queryset(self):
        return Course.objects.all().order_by("id")


class ApplicantCoursesListAPI(generics.ListAPIView):
    """
    List of available courses for the applicant.
    GET /api/applicant/courses/
    """

    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]
    serializer_class = ApplicantCourseSerializer

    def get_queryset(self):
        return Course.objects.all().order_by("id")


class ApplicantBalanceAPI(APIView):
    """
    Applicant lesson balance.
    GET /api/applicant/balance/
    """

    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]

    def get(self, request):
        bal, _ = LessonBalance.objects.get_or_create(student=request.user)
        ser = ApplicantBalanceSerializer(bal)
        return Response(ser.data)


class ApplicantPaymentsListAPI(generics.ListAPIView):
    """
    Applicant payment history.
    GET /api/applicant/payments/
    """

    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]
    serializer_class = ApplicantPaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(student=self.request.user).order_by("-paid_at")


class ApplicantCreatePaymentAPI(APIView):
    """
    Legacy endpoint intentionally disabled.
    Use /api/payments/create/ for automatic YooKassa payments.
    """

    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]

    def post(self, request):
        return Response(
            {"detail": "legacy manual payment creation is disabled; use /api/payments/create/"},
            status=410,
        )


class ApplicantCreateClientRequestAPI(APIView):
    """
    Create a client request for the manager.
    POST /api/applicant/requests/create/
    """

    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]

    def post(self, request):
        ser = ApplicantClientRequestCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        request_obj = ser.save()
        return Response(
            {
                "id": request_obj.id,
                "comment": request_obj.comment,
                "status": request_obj.status,
                "created_at": request_obj.created_at,
            },
            status=201,
        )
