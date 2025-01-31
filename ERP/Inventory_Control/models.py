from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum, Avg
from datetime import datetime, timedelta


class Product(models.Model):
    ProductId = models.AutoField(primary_key=True, unique=True)
    ProductName = models.CharField(max_length=200)
    Category = models.CharField(max_length=100)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    StockLevel = models.IntegerField()
    ReorderLevel = models.IntegerField()
    LastPurchaseDate = models.DateField(null=True, blank=True)
    SupplierId = models.ForeignKey(
        "Procurement.Supplier",
        null=True,
        related_name="products",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return (
            f"{self.ProductName} - Level:{self.StockLevel} Order at:{self.ReorderLevel}"
        )

    def GetAllStores(self):
        """
        Returns all stores that stock this product.
        """
        return self.stocklocation_set.values("StoreId__StoreName", "StoreId__Location")

    def GetStockLevel(self):
        """
        Returns the total stock level for this product across all stores.
        """
        return (
            self.stocklocation_set.aggregate(TotalStock=Sum("Quantity"))["TotalStock"]
            or 0
        )

    def TransferStock(self, from_store, to_store, quantity):
        """
        Transfers stock of this product between stores.
        from_store: Store instance to transfer from.
        to_store: Store instance to transfer to.
        quantity: Quantity of stock to transfer.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        from_stock = self.stocklocation.filter(StoreId=from_store).first()
        to_stock = self.stocklocation.filter(StoreId=to_store).first()

        if not from_stock or from_stock.Quantity < quantity:
            raise ValidationError("Insufficient stock in the source store.")

        from_stock.Quantity -= quantity
        from_stock.save()

        if to_stock:
            to_stock.Quantity += quantity
        else:
            StockLocation.objects.create(
                ProductId=self, StoreId=to_store, Quantity=quantity
            )
        to_stock.save()

    def EditReorderLevel(self, new_reorder_level):
        """
        Updates the reorder level for this product.
        new_reorder_level: New reorder level (integer).
        """
        if new_reorder_level < 0:
            raise ValueError("Reorder level must be a non-negative integer.")
        self.ReorderLevel = new_reorder_level
        self.save()


class Store(models.Model):
    StoreId = models.AutoField(primary_key=True, unique=True)
    StoreName = models.CharField(max_length=200)
    Location = models.CharField(max_length=200)
    ContactNumber = models.CharField(max_length=15)
    ManagerId = models.OneToOneField(
        "HR.Staff",
        null=True,
        on_delete=models.SET_NULL,
    )
    TotalSales = models.IntegerField()
    OperatingHours = models.IntegerField()

    def __str__(self):
        return f"{self.StoreName} - {self.Location}"

    def GetAllProducts(self):
        """
        Returns all products stocked in this store.
        """
        return self.stocklocation_set.values("ProductId__ProductName", "Quantity")

    def ViewStorePerformance(self):
        """
        Returns the store's performance metrics.
        """
        return {
            "TotalSales": self.TotalSales,
            "AverageSalesPerHour": (
                self.TotalSales / self.OperatingHours if self.OperatingHours else 0
            ),
        }

    def edit_store_data(self, **kwargs):
        """
        Updates store information with provided data.
        Args:
            **kwargs: Dictionary of fields to update and their new values
        Returns:
            bool: True if update successful, raises exception otherwise
        """
        try:
            valid_fields = {
                "StoreName",
                "Location",
                "ContactNumber",
                "ManagerId",
                "OperatingHours",
            }
            # Filter out invalid fields
            update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
            if not update_data:
                raise ValidationError("No valid fields provided for update")

            # Validate contact number format if it's being updated
            if "ContactNumber" in update_data:
                if not update_data["ContactNumber"].replace("+", "").isdigit():
                    raise ValidationError("Invalid contact number format")

            # Validate operating hours if being updated
            if "OperatingHours" in update_data:
                if not 0 < update_data["OperatingHours"] <= 24:
                    raise ValidationError("Operating hours must be between 1 and 24")

            # Update the fields
            for field, value in update_data.items():
                setattr(self, field, value)
            self.full_clean()  # Validate all fields
            self.save()
            return True

        except ValidationError as ve:
            raise ValidationError(f"Validation error: {str(ve)}")
        except Exception as e:
            raise ValueError(f"Error updating store data: {str(e)}")


class StockLocation(models.Model):
    StockLocationId = models.AutoField(primary_key=True, unique=True)
    ProductId = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stocklocation"
    )
    StoreId = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="stocklocation"
    )
    Quantity = models.IntegerField()
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ProductId.ProductName} - {self.StoreId.StoreName} - Amount: {self.Quantity}"

    def AdjustStock(self, quantity):
        """
        Adjusts the stock quantity for this stock location.
        quantity: Positive to increase stock, negative to decrease stock.
        """
        if self.Quantity + quantity < 0:
            raise ValidationError("Insufficient stock for the operation.")
        self.Quantity += quantity
        self.save()
