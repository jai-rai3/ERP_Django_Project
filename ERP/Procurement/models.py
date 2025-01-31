from django.db import models
from Inventory_Control.models import Product
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta


class Supplier(models.Model):
    SupplierId = models.AutoField(primary_key=True, unique=True)
    SupplierName = models.CharField(max_length=200)
    ContactDetails = models.CharField(max_length=200)
    Location = models.CharField(max_length=200)
    ContractTerms = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.SupplierName} - {self.Location}"

    def GetSupplierProducts(self):
        """
        Retrieves all products associated with the supplier.
        """
        return Product.objects.filter(SupplierId=self.SupplierId)

    def SetSupplierData(self, **kwargs):
        """
        Updates the supplier's data.
        :param kwargs: Dictionary of field names and their new values.
        """
        allowed_fields = {"SupplierName", "ContactDetails", "Location", "ContractTerms"}
        for field, value in kwargs.items():
            if field not in allowed_fields:
                raise ValueError(f"Invalid field: {field}")
            setattr(self, field, value)
        self.save()

    def ViewSupplierPerformance(self, dateRange=30):
        """
        Analyses the supplier's performance based on delivered orders over a specified period.
        :param dateRange: The number of days to consider for the analysis.
        :return: Performance metrics.
        """
        endDate = datetime.now()
        startDate = endDate - timedelta(days=dateRange)

        orders = PurchaseOrder.objects.filter(
            ProductId__SupplierId=self.SupplierId,
            DeliveryDate__range=[startDate, endDate],
            OrderStatus="Delivered",
        )

        totalAmount = orders.aggregate(total=Sum("TotalAmount"))["total"] or 0
        totalOrders = orders.count()

        performance = {
            "TotalDeliveredOrders": totalOrders,
            "TotalDeliveredAmount": totalAmount,
            "AverageOrderValue": totalAmount / totalOrders if totalOrders > 0 else 0,
        }
        return performance


class PurchaseOrder(models.Model):
    PurchaseOrderId = models.AutoField(primary_key=True, unique=True)
    TotalAmount = models.IntegerField()
    ProductId = models.ForeignKey(Product, on_delete=models.CASCADE)
    OrderDate = models.DateField(auto_now_add=True)
    DeliveryDate = models.DateField(blank=True, null=True)
    OrderStatus = models.CharField(max_length=200)

    def __str__(self):
        return f"Id:{self.PurchaseOrderId} - Contains:{self.ProductId.ProductName} - Amount:{self.TotalAmount} - Status:{self.OrderStatus}"

    @classmethod
    def CreatePurchaseOrder(
        cls, product, totalAmount, deliveryDate, orderStatus="Pending"
    ):
        """
        Creates a new purchase order.
        :param product: Product instance to be ordered.
        :param totalAmount: Total amount of the purchase.
        :param deliveryDate: Expected delivery date.
        :param orderStatus: Status of the order. Default is 'Pending'.
        """
        return cls.objects.create(
            ProductId=product,
            TotalAmount=totalAmount,
            DeliveryDate=deliveryDate,
            OrderStatus=orderStatus,
        )

    def GetPurchaseOrderStatus(self):
        """
        Retrieves the current status of the purchase order.
        """
        return self.OrderStatus

    def SetPurchaseOrder(self, **kwargs):
        """
        Updates the purchase order's details.
        :param kwargs: Dictionary of field names and their new values.
        """
        allowed_fields = {"TotalAmount", "DeliveryDate", "OrderStatus"}
        for field, value in kwargs.items():
            if field not in allowed_fields:
                raise ValueError(f"Invalid field: {field}")
            setattr(self, field, value)
        self.save()
