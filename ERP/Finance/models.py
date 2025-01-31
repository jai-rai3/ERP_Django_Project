from django.db import models


class Department(models.Model):
    DepartmentId = models.AutoField(primary_key=True, unique=True)
    DepartmentName = models.CharField(max_length=200)
    ManagerId = models.OneToOneField(
        "HR.Staff",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="department",
    )
    Budget = models.IntegerField()

    def __str__(self):
        if self.ManagerId:
            return f"{self.DepartmentName} - Manager: {self.ManagerId.StaffName}"
        return f"{self.DepartmentName}"

    def GetDepartmentBudget(self):
        """
        Returns the budget allocated to the department.
        """
        return self.Budget

    def SetDepartmentBudget(self, budget):
        """
        Sets a new budget for the department.
        budget: New budget value (integer).
        """
        if isinstance(budget, int) and budget >= 0:
            self.Budget = budget
            self.save()
        else:
            raise ValueError("Budget must be a non-negative integer.")

    def GetDepartmentStaff(self):
        """
        Returns all staff members belonging to the department.
        Assumes there is a related_name 'staff' set for the ForeignKey in the Staff model.
        """
        return self.staff.all()
