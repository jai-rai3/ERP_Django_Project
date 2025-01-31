from Inventory_Control import Product
from Procurement import Supplier, PurchaseOrder
from Sales.models import Sales
from Inventory_Control.models import Product, Store


class Facade():

    def __init__(self):
        self.sales = Sales.objects.all()
        self.stores = Store.objects.all()
        self.products = Product.objects.all()

    def TriggerPurchaseOrder(self, productId):
        """
        Triggers a purchase order if the stock level of a product is below its reorder level.

        productId: The ID of the product to check.
        return: A message indicating the result of the operation.
        """
        try:
            # Fetch the product
            product = Product.objects.get(ProductId=productId)

            # Get the current stock level for the product
            currentStock = product.GetStockLevel()

            # Check if stock is below reorder level
            if currentStock < product.ReorderLevel:
                # Fetch all associated suppliers for the product
                supplier = Supplier.objects.get(SupplierId=product.SupplierId.SupplierId)

                if not supplier.exists():
                    return f"No supplier found for product ID {productId}."

                # Determine the reorder quantity (e.g., reorder to full stock level)
                reorderQuantity = product.ReorderLevel - currentStock
                totalAmount = reorderQuantity * product.Price

                # Create a new purchase order
                purchaseOrder = PurchaseOrder.CreatePurchaseOrder(
                    product=product,
                    totalAmount=totalAmount,
                    orderStatus="Pending",
                    supplierId = supplier
                )

                return f"Purchase order {purchaseOrder.PurchaseOrderId} created for product ID {productId} with quantity {reorderQuantity}."

            else:
                return f"Stock level ({currentStock}) for product ID {productId} is sufficient. No purchase order needed."

        except Product.DoesNotExist:
            return f"Product ID {productId} does not exist."

        except Exception as e:
            return f"Error triggering purchase order: {str(e)}"


    def ViewSalesPerformance(self, start_date=None, end_date=None):
        """
        Retrieves sales data for graphing performance by stores and products over time.
        :param start_date: Optional start date for filtering sales (datetime.date).
        :param end_date: Optional end date for filtering sales (datetime.date).
        :return: A dictionary with store-wise and product-wise sales performance data.
        """
        try:
            from django.db.models import Sum

            sales_queryset = self.sales
            if start_date:
                sales_queryset = sales_queryset.filter(DateOfSale__gte=start_date)
            if end_date:
                sales_queryset = sales_queryset.filter(DateOfSale__lte=end_date)

            # Aggregate sales data by store
            store_sales = (
                sales_queryset.values("StoreId__StoreName")
                .annotate(TotalSales=Sum("TotalAmount"))
                .order_by("StoreId__StoreName")
            )

            # Aggregate sales data by product
            product_sales = (
                sales_queryset.values("StoreId__StoreName", "ProductId__ProductName")
                .annotate(TotalSales=Sum("TotalAmount"))
                .order_by("ProductId__ProductName")
            )

            return {"store_sales": list(store_sales), "product_sales": list(product_sales)}

        except Exception as e:
            raise ValueError(f"Error generating sales performance graph: {str(e)}")
