from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect

from ..forms import ReviewForm
from ..models import Farm, Review


@login_required
def submit_review(request: HttpRequest, slug: str) -> HttpResponse:
    """Create or update a farm review for the current customer."""
    farm = get_object_or_404(Farm, slug=slug)

    if not getattr(request.user, "is_customer", False):
        return HttpResponse("Only customer accounts can submit reviews.", status=403)

    if request.method != "POST":
        return redirect("farm_detail", slug=slug)

    existing = Review.objects.filter(farm=farm, customer=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.farm = farm
        review.customer = request.user
        if review.rating < 1:
            review.rating = 1
        if review.rating > 5:
            review.rating = 5
        review.save()
    return redirect("farm_detail", slug=slug)


