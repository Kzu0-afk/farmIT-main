# 🗺️ Mapping Integration Plan for FarmIT Delivery System

## 📋 Current Status

### What's Already Implemented
- ✅ Mapbox GL JS integration code exists in `delivery_quote.html`
- ✅ Farm and Address models have `latitude` and `longitude` fields
- ✅ Haversine formula for distance calculation (straight-line)
- ✅ Delivery quote calculation based on distance
- ❌ **Map not displaying** - `MAPBOX_PUBLIC_TOKEN` environment variable missing
- ❌ **No actual routing** - Only shows straight line between points, not road-based route

### Issues to Fix
1. Map not showing (missing API token)
2. No actual routing (only straight-line distance)
3. Need proper route visualization from farm to delivery address

---

## 🎯 Recommended Solution: OpenRouteService (ORS)

### Why OpenRouteService?
- ✅ **Free tier**: 2,000 requests/day (sufficient for MVP)
- ✅ **No credit card required** for free tier
- ✅ **Open-source routing engine** (Valhalla) with OpenStreetMap data
- ✅ **RESTful API** - Easy to integrate with Django
- ✅ **Multiple routing profiles**: driving, cycling, walking, heavy vehicles
- ✅ **Route optimization** and turn-by-turn directions
- ✅ **Geocoding included** (address to coordinates)
- ✅ **Well-documented** and actively maintained

### Alternative Options (Comparison)

| Solution | Type | Cost | Setup Complexity | Routing Quality | Best For |
|----------|------|------|------------------|-----------------|----------|
| **OpenRouteService** | API Service | Free (2K/day) | ⭐ Easy | ⭐⭐⭐⭐ Excellent | **Recommended** |
| **OSRM** | Self-hosted | Free | ⭐⭐⭐ Complex | ⭐⭐⭐⭐ Excellent | High traffic, self-hosted |
| **GraphHopper** | API/Self-hosted | Free tier / Self-hosted | ⭐⭐ Medium | ⭐⭐⭐⭐ Excellent | Enterprise scale |
| **Mapbox Directions API** | Commercial | $0.50/1K requests | ⭐ Easy | ⭐⭐⭐⭐⭐ Best | Budget available |
| **Leaflet + OSM** | Map Display Only | Free | ⭐ Easy | ❌ No routing | Display only |

### Decision: **OpenRouteService + Leaflet**

**Rationale:**
- Best balance of free tier, ease of integration, and routing quality
- No self-hosting required (unlike OSRM)
- Better free tier than Mapbox for routing
- Leaflet for map display (lightweight, open-source)

---

## 📐 Architecture Plan

### Components Needed

1. **Backend (Django)**
   - New utility module: `farmIT/products/utils/routing.py`
   - Function to call OpenRouteService Directions API
   - Cache routing results (optional, for performance)
   - Update `estimate_distance_and_fee()` to use actual route distance

2. **Frontend (Template)**
   - Replace Mapbox with **Leaflet** (open-source map library)
   - Use **OpenRouteService Directions API** for route geometry
   - Display route polyline on map
   - Show markers for farm and delivery address

3. **Environment Variables**
   - `OPENROUTESERVICE_API_KEY` (get free from openrouteservice.org)
   - Remove dependency on `MAPBOX_PUBLIC_TOKEN` (or keep as optional fallback)

---

## 🔧 Implementation Steps

### Step 1: Get OpenRouteService API Key
1. Go to https://openrouteservice.org/
2. Sign up for free account
3. Get API key from dashboard
4. Free tier: 2,000 requests/day

### Step 2: Backend Integration

**File: `farmIT/products/utils/routing.py`** (new file)
```python
import requests
from typing import Optional, Tuple, List
from django.conf import settings

def get_route(
    start_lat: float, 
    start_lon: float, 
    end_lat: float, 
    end_lon: float,
    profile: str = "driving-car"  # Options: driving-car, driving-hgv, cycling-regular, foot-walking
) -> Optional[dict]:
    """
    Get route from OpenRouteService Directions API.
    Returns route geometry, distance (meters), and duration (seconds).
    """
    api_key = getattr(settings, 'OPENROUTESERVICE_API_KEY', None)
    if not api_key:
        return None
    
    url = "https://api.openrouteservice.org/v2/directions/" + profile
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [[start_lon, start_lat], [end_lon, end_lat]],
        "format": "geojson"
    }
    
    try:
        response = requests.post(url, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Log error, return None for fallback to Haversine
        return None

def get_route_distance_km(
    start_lat: float, 
    start_lon: float, 
    end_lat: float, 
    end_lon: float
) -> Optional[float]:
    """Get route distance in kilometers."""
    route = get_route(start_lat, start_lon, end_lat, end_lon)
    if route and 'features' in route and len(route['features']) > 0:
        properties = route['features'][0].get('properties', {})
        summary = properties.get('summary', {})
        distance_m = summary.get('distance', 0)
        return round(distance_m / 1000, 2)  # Convert to km
    return None
```

**File: `farmIT/products/models.py`** (update `estimate_distance_and_fee`)
```python
from .utils.routing import get_route_distance_km

def estimate_distance_and_fee(...):
    # Try to get actual route distance first
    route_distance = get_route_distance_km(
        farm.latitude, farm.longitude,
        address.latitude, address.longitude
    )
    
    if route_distance:
        distance_km = Decimal(str(route_distance))
    else:
        # Fallback to Haversine if API fails
        distance_km = _haversine_km(...)
    
    # Rest of calculation...
```

### Step 3: Frontend Integration

**File: `farmIT/templates/products/delivery_quote.html`** (replace map section)

Replace Mapbox code with Leaflet + OpenRouteService:

```html
<!-- Leaflet CSS & JS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<div id="delivery-map" class="w-full h-72 rounded-xl overflow-hidden border border-gray-200"></div>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const farmCoords = [{{ farm.latitude }}, {{ farm.longitude }}];
  const addrCoords = [{{ address.latitude }}, {{ address.longitude }}];
  
  // Initialize Leaflet map
  const map = L.map('delivery-map').setView(
    [(farmCoords[0] + addrCoords[0]) / 2, (farmCoords[1] + addrCoords[1]) / 2],
    10
  );
  
  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  
  // Add markers
  const farmMarker = L.marker(farmCoords, { icon: L.divIcon({ 
    className: 'custom-marker',
    html: '<div style="background: #15803d; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
    iconSize: [20, 20]
  })}).addTo(map).bindPopup('{{ farm.name|escapejs }}');
  
  const addrMarker = L.marker(addrCoords, { icon: L.divIcon({ 
    className: 'custom-marker',
    html: '<div style="background: #f97316; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
    iconSize: [20, 20]
  })}).addTo(map).bindPopup('{{ address.label|escapejs }}');
  
  // Fetch route from backend (via AJAX or pass route data from Django view)
  fetch('{% url "delivery_route_geojson" product.id %}?address_id={{ address.id }}')
    .then(response => response.json())
    .then(data => {
      if (data.route) {
        // Add route polyline
        const routeLayer = L.geoJSON(data.route, {
          style: {
            color: '#15803d',
            weight: 4,
            opacity: 0.8
          }
        }).addTo(map);
        
        // Fit bounds to show entire route
        map.fitBounds(routeLayer.getBounds(), { padding: [40, 40] });
      } else {
        // Fallback: show straight line if routing fails
        const straightLine = L.polyline([farmCoords, addrCoords], {
          color: '#15803d',
          weight: 2,
          dashArray: '5, 10',
          opacity: 0.5
        }).addTo(map);
        map.fitBounds([[farmCoords[0], farmCoords[1]], [addrCoords[0], addrCoords[1]]], { padding: [40, 40] });
      }
    })
    .catch(error => {
      console.error('Route fetch failed:', error);
      // Fallback to straight line
      const straightLine = L.polyline([farmCoords, addrCoords], {
        color: '#15803d',
        weight: 2,
        dashArray: '5, 10',
        opacity: 0.5
      }).addTo(map);
      map.fitBounds([[farmCoords[0], farmCoords[1]], [addrCoords[0], addrCoords[1]]], { padding: [40, 40] });
    });
});
</script>
```

### Step 4: Add Route Endpoint

**File: `farmIT/products/views/address_delivery.py`** (add new view)

```python
from django.http import JsonResponse
from .utils.routing import get_route

@login_required
def delivery_route_geojson(request: HttpRequest, product_id: int) -> JsonResponse:
    """Return route GeoJSON for map display."""
    if not getattr(request.user, "is_customer", False):
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    product = get_object_or_404(Product, pk=product_id, is_approved=True)
    farm = product.farm or getattr(product.farmer, "farm", None)
    if not farm or not farm.latitude or not farm.longitude:
        return JsonResponse({"error": "Farm coordinates missing"}, status=400)
    
    address_id = request.GET.get("address_id")
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    if not address.latitude or not address.longitude:
        return JsonResponse({"error": "Address coordinates missing"}, status=400)
    
    route = get_route(
        farm.latitude, farm.longitude,
        address.latitude, address.longitude
    )
    
    if route and 'features' in route:
        return JsonResponse({"route": route['features'][0]})
    else:
        return JsonResponse({"route": None})
```

**File: `farmIT/products/urls.py`** (add URL pattern)
```python
path("deliveries/quote/<int:product_id>/route.geojson", views.delivery_route_geojson, name="delivery_route_geojson"),
```

### Step 5: Environment Configuration

**File: `farmIT/.env`** (add)
```
OPENROUTESERVICE_API_KEY=your_api_key_here
```

**File: `farmIT/farmIT/settings/base.py`** (add)
```python
OPENROUTESERVICE_API_KEY = os.getenv('OPENROUTESERVICE_API_KEY', '')
```

### Step 6: Update View to Pass Route Data

**File: `farmIT/products/views/address_delivery.py`** (update `delivery_quote` view)

Optionally pass route GeoJSON directly to template (alternative to AJAX):

```python
from .utils.routing import get_route

def delivery_quote(...):
    # ... existing code ...
    
    route_geojson = None
    if address and farm.latitude and farm.longitude and address.latitude and address.longitude:
        route = get_route(
            farm.latitude, farm.longitude,
            address.latitude, address.longitude
        )
        if route and 'features' in route:
            route_geojson = route['features'][0]
    
    return render(..., {
        # ... existing context ...
        "route_geojson": route_geojson,
    })
```

---

## 📦 Dependencies

### Python Packages
```bash
pip install requests  # For API calls (likely already installed)
```

### Frontend Libraries (CDN)
- Leaflet 1.9.4 (CSS + JS) - Map display
- OpenStreetMap tiles (free, no API key needed)

### API Service
- OpenRouteService API key (free registration)

---

## ✅ Testing Checklist

- [ ] OpenRouteService API key configured
- [ ] Route API endpoint returns GeoJSON
- [ ] Map displays with Leaflet
- [ ] Route polyline shows on map
- [ ] Markers display correctly (farm = green, address = orange)
- [ ] Map bounds fit route properly
- [ ] Fallback to straight line if API fails
- [ ] Distance calculation uses route distance (not Haversine)
- [ ] ETA calculation updated based on route
- [ ] Works on mobile devices
- [ ] Error handling for missing coordinates
- [ ] Rate limiting respected (2K requests/day)

---

## 🚀 Deployment Considerations

### Vercel Environment Variables
Add to Vercel dashboard:
```
OPENROUTESERVICE_API_KEY=your_api_key_here
```

### Rate Limiting
- Free tier: 2,000 requests/day
- Consider caching route results for same origin/destination pairs
- Monitor usage in OpenRouteService dashboard

### Fallback Strategy
- If API fails or quota exceeded, fall back to:
  1. Haversine distance calculation
  2. Straight-line visualization on map
  3. Show message: "Route preview unavailable, using straight-line distance"

---

## 📊 Cost Analysis

| Solution | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **OpenRouteService** | 2,000/day | €49/month (20K/day) | **Recommended** |
| Mapbox | 100K/month | $0.50/1K requests | Higher budget |
| OSRM | Unlimited (self-hosted) | Server costs | High traffic |

**For FarmIT MVP:** OpenRouteService free tier (2K/day) is sufficient.

---

## 🎯 Success Criteria

1. ✅ Map displays correctly with farm and delivery address markers
2. ✅ Route polyline shows actual road-based path (not straight line)
3. ✅ Distance calculation uses route distance
4. ✅ ETA calculation based on route duration
5. ✅ Graceful fallback if API unavailable
6. ✅ Mobile-responsive map display
7. ✅ No breaking changes to existing delivery flow

---

## 📝 Next Steps

1. **Get OpenRouteService API key** (5 minutes)
2. **Implement backend routing utility** (1-2 hours)
3. **Update frontend with Leaflet** (2-3 hours)
4. **Test and debug** (1-2 hours)
5. **Deploy to Vercel** (30 minutes)

**Total Estimated Time:** 5-8 hours

---

## 🔗 Resources

- OpenRouteService: https://openrouteservice.org/
- OpenRouteService API Docs: https://openrouteservice.org/dev/#/api-docs
- Leaflet Documentation: https://leafletjs.com/
- OpenStreetMap: https://www.openstreetmap.org/

---

**Status:** Ready for implementation  
**Priority:** High (fixes critical delivery mapping issue)  
**Complexity:** Medium

