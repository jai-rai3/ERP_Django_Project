from django.db import models
from Inventory_Control.models import Store, Product
from Human_Resources.models import Staff


class Sales(models.Model):
    SalesId = models.AutoField(primary_key=True, unique=True)
    PaymentMethod = models.CharField(max_length=200)
    TotalAmount = models.DecimalField(max_digits=15, decimal_places=2)
    StoreId = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="sales")
    ProductId = models.ForeignKey(
        Product, on_delete=models.SET_NULL, related_name="sales", null=True
    )
    StaffId = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, related_name="sales"
    )
    DateOfSale = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Id: {self.SalesId} - Total: {self.TotalAmount} - Store: {self.StoreId.StoreName}"

    def GetSalesData(self):
        """
        Returns the sales record data as a dictionary.
        """
        return {
            "SalesId": self.SalesId,
            "PaymentMethod": self.PaymentMethod,
            "TotalAmount": self.TotalAmount,
            "Store": self.StoreId.StoreName,
            "Staff": self.StaffId.StaffName if self.StaffId else None,
            "DateOfSale": self.DateOfSale,
        }

    def GetSalesGraph(self, start_date=None, end_date=None):
        """
        Generates sales data for a graph based on the given date range.
        start_date: Optional start date for filtering sales (datetime.date).
        end_date: Optional end date for filtering sales (datetime.date).
        """
        from django.db.models import Sum

        sales_queryset = Sales.objects.all()

        if start_date:
            sales_queryset = sales_queryset.filter(DateOfSale__gte=start_date)
        if end_date:
            sales_queryset = sales_queryset.filter(DateOfSale__lte=end_date)

        sales_summary = (
            sales_queryset.values("DateOfSale")
            .annotate(TotalSales=Sum("TotalAmount"))
            .order_by("DateOfSale")
        )

        return list(sales_summary)  # Returns a list of dictionaries for graph plotting

    def CalculateTotalSales(self, start_date=None, end_date=None):
        """
        Calculates the total sales amount within the specified date range.
        start_date: Optional start date for filtering sales (datetime.date).
        end_date: Optional end date for filtering sales (datetime.date).
        """
        from django.db.models import Sum

        sales_queryset = Sales.objects.all()

        if start_date:
            sales_queryset = sales_queryset.filter(DateOfSale__gte=start_date)
        if end_date:
            sales_queryset = sales_queryset.filter(DateOfSale__lte=end_date)

        total_sales = sales_queryset.aggregate(TotalSales=Sum("TotalAmount"))
        return total_sales["TotalSales"] or 0
