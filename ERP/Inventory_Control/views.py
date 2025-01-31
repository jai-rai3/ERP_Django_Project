from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ERP.facade import Facade
from Inventory_Control.models import Product
import json


@csrf_exempt
def trigger_purchase_order(request):
    """
    Function-based view to trigger a purchase order for a product.

    :param request: The HTTP request object.
    :return: A JsonResponse indicating the success or failure of the operation.
    """
    if request.method == "POST":
        try:
            # Parse the request body to get product ID
            body = json.loads(request.body)
            product_id = body.get("productId")

            if not product_id:
                return JsonResponse({"error": "Product ID is required."}, status=400)

            # Instantiate the facade
            facade = Facade()

            # Call the TriggerPurchaseOrder function
            result_message = facade.TriggerPurchaseOrder(productId=int(product_id))

            # Return success response
            return JsonResponse({"message": result_message}, status=200)
        # Errors
        except Product.DoesNotExist:
            return JsonResponse(
                {"error": f"Product ID {product_id} does not exist."}, status=404
            )
        # Errors
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        # Errors
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    # If not POST, return method not allowed
    return JsonResponse({"error": "Only POST method is allowed."}, status=405)
