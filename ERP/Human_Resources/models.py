from django.db import models
from Finance.models import Department
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta


class Staff(models.Model):
    StaffId = models.AutoField(primary_key=True, unique=True)
    StaffName = models.CharField(max_length=200)
    Role = models.CharField(max_length=200)
    Salary = models.IntegerField()
    DepartmentId = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff",  # Ensure related_name is added
    )
    HireDate = models.DateField(auto_now_add=True)

    def __str__(self):
        if self.DepartmentId:
            return f"{self.StaffName} - Role: {self.Role} - In: {self.DepartmentId.DepartmentName}"
        return f"{self.StaffName} - Role: {self.Role}"

    def GetStaffData(self):
        """
        Returns the staff member's data as a dictionary.
        """
        return {
            "StaffId": self.StaffId,
            "StaffName": self.StaffName,
            "Role": self.Role,
            "Salary": self.Salary,
            "Department": (
                self.DepartmentId.DepartmentName if self.DepartmentId else None
            ),
            "HireDate": self.HireDate,
        }

    def EditStaffData(self, **kwargs):
        """Edits the staff member's data.
        kwargs: Dictionary of field names and their new values.
                    Valid keys: 'StaffName', 'Role', 'Salary'."""

        # Define valid fields
        valid_fields = {"StaffName", "Role", "Salary"}

        # Filter out invalid fields from kwargs
        update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
        if not update_data:
            raise ValueError("No valid fields provided for update")

        # Validate Salary if being updated
        if "Salary" in update_data:
            if not (
                isinstance(update_data["Salary"], int) and update_data["Salary"] >= 0
            ):
                raise ValueError("Salary must be a non-negative integer.")

        # Update the fields
        for field, value in update_data.items():
            setattr(self, field, value)

        self.full_clean()  # Validate all fields
        self.save()

    def ViewPerformance(self, date_range=30):
        """
        Analyzes performance metrics for a staff member over a specified period.
        Args:
            date_range (int): Number of days to analyze (default: 30)
        Returns:
            dict: Performance metrics including total sales, average daily sales, etc.
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)

            # Assuming Sales model with StaffId relation and total_amount field
            sales_data = Staff.sales.filter(
                StaffId=self.StaffId, SalesDate__range=[start_date, end_date]
            ).aggregate(
                total_sales=Sum("total_amount"),
                average_daily_sales=Avg("total_amount"),
                total_transactions=Count("id"),
            )

            # Calculate additional metrics
            performance_metrics = {
                "staff_name": self.StaffName,
                "period_total_sales": sales_data["total_sales"] or 0,
                "average_daily_sales": sales_data["average_daily_sales"] or 0,
                "total_transactions": sales_data["total_transactions"] or 0,
                "sales_per_day": (sales_data["total_sales"] or 0) / date_range,
                "performance_index": (sales_data["total_sales"] or 0)
                / (self.Salary or 1),  # Normalise by salary
            }

            return performance_metrics

        except Exception as e:
            raise ValueError(f"Error calculating staff performance: {str(e)}")

    def AssignDepartment(self, DepartmentId):
        """
        Assigns the staff member to a department.
        DepartmentId: The department instance to assign.
        """
        if isinstance(DepartmentId, Department):
            self.DepartmentId = DepartmentId
            self.save()
        else:
            raise ValueError("Invalid department instance.")
