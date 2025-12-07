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

## 🎨 UI Improvements & Optimization

### Visual Enhancements

#### 1. **Enhanced Map Styling**
- **Custom Marker Icons**: Use branded icons for farm (🌾) and delivery address (📦)
- **Route Visualization**: 
  - Animated route drawing effect on load
  - Color-coded route segments (green for efficient, yellow for moderate, red for long routes)
  - Gradient polyline for better visual appeal
- **Map Theme**: Match FarmIT's green/amber color scheme
- **Shadow Effects**: Add subtle shadows to markers for depth

```html
<!-- Enhanced marker styling -->
<style>
  .farm-marker {
    background: linear-gradient(135deg, #15803d 0%, #16a34a 100%);
    border: 3px solid white;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3), 0 0 0 2px rgba(21, 128, 61, 0.2);
    animation: pulse 2s infinite;
  }
  
  .delivery-marker {
    background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
    border: 3px solid white;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3), 0 0 0 2px rgba(249, 115, 22, 0.2);
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
</style>
```

#### 2. **Loading States & Skeleton UI**
- **Map Loading Indicator**: Show spinner or skeleton while route is being fetched
- **Progressive Loading**: Display map first, then load route asynchronously
- **Smooth Transitions**: Fade-in animations for route and markers

```html
<div id="delivery-map" class="relative">
  <div id="map-loading" class="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-xl z-10">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-2"></div>
      <p class="text-gray-600 text-sm">Loading route...</p>
    </div>
  </div>
</div>
```

#### 3. **Interactive Features**
- **Route Information Panel**: 
  - Distance in km/miles toggle
  - Estimated delivery time
  - Route summary (toll roads, highway usage)
- **Map Controls**: 
  - Fullscreen mode
  - Zoom to route button
  - Reset view button
- **Marker Tooltips**: Rich popups with farm/address details
- **Route Comparison**: Show alternative routes if available

```html
<!-- Route info panel -->
<div class="bg-white/95 backdrop-blur-sm rounded-lg p-4 shadow-lg border border-gray-200 mt-4">
  <div class="flex items-center justify-between mb-2">
    <h3 class="font-semibold text-gray-900">Route Details</h3>
    <button id="toggle-route-info" class="text-gray-500 hover:text-gray-700">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
      </svg>
    </button>
  </div>
  <div id="route-info-content" class="space-y-2">
    <div class="flex items-center text-sm">
      <span class="text-gray-600 w-24">Distance:</span>
      <span class="font-semibold text-green-700" id="route-distance">{{ distance_km }} km</span>
    </div>
    <div class="flex items-center text-sm">
      <span class="text-gray-600 w-24">Duration:</span>
      <span class="font-semibold text-orange-600" id="route-duration">{{ estimated_time }}</span>
    </div>
  </div>
</div>
```

#### 4. **Error Handling UI**
- **Graceful Degradation**: 
  - Clear message when route API fails
  - Visual indicator for straight-line fallback
  - Retry button for failed requests
- **User-Friendly Messages**: 
  - "Unable to load route preview" instead of technical errors
  - Helpful suggestions (check internet connection, try again)

```html
<div id="route-error" class="hidden bg-amber-50 border border-amber-200 rounded-lg p-4 mt-4">
  <div class="flex items-start">
    <svg class="w-5 h-5 text-amber-600 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
    </svg>
    <div class="flex-1">
      <p class="text-sm font-medium text-amber-800">Route preview unavailable</p>
      <p class="text-sm text-amber-700 mt-1">Using straight-line distance estimate. Delivery fee calculated accurately.</p>
      <button onclick="retryRoute()" class="mt-2 text-sm text-amber-800 hover:text-amber-900 underline">Try again</button>
    </div>
  </div>
</div>
```

### Mobile Optimization

#### 1. **Responsive Design**
- **Touch-Friendly Controls**: Larger tap targets for mobile
- **Swipe Gestures**: Swipe to dismiss route info panel
- **Mobile Map Height**: Adjustable height (50vh on mobile, fixed on desktop)
- **Bottom Sheet**: Route info as bottom sheet on mobile devices

```css
@media (max-width: 768px) {
  #delivery-map {
    height: 50vh;
    min-height: 300px;
  }
  
  .route-info-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    max-height: 50vh;
    border-radius: 1rem 1rem 0 0;
  }
}
```

#### 2. **Performance Optimizations**
- **Lazy Loading**: Load map only when visible
- **Tile Caching**: Cache map tiles for offline viewing
- **Debounced Route Requests**: Prevent multiple simultaneous requests
- **Route Result Caching**: Cache route results in localStorage for same origin/destination

```javascript
// Route caching example
function getCachedRoute(origin, destination) {
  const cacheKey = `route_${origin.lat}_${origin.lng}_${destination.lat}_${destination.lng}`;
  const cached = localStorage.getItem(cacheKey);
  if (cached) {
    const data = JSON.parse(cached);
    // Cache valid for 1 hour
    if (Date.now() - data.timestamp < 3600000) {
      return data.route;
    }
  }
  return null;
}

function cacheRoute(origin, destination, route) {
  const cacheKey = `route_${origin.lat}_${origin.lng}_${destination.lat}_${destination.lng}`;
  localStorage.setItem(cacheKey, JSON.stringify({
    route: route,
    timestamp: Date.now()
  }));
}
```

#### 3. **Accessibility Improvements**
- **Keyboard Navigation**: Full keyboard support for map controls
- **Screen Reader Support**: ARIA labels for markers and route info
- **High Contrast Mode**: Alternative color scheme for accessibility
- **Focus Indicators**: Clear focus states for interactive elements

```html
<!-- Accessible map controls -->
<div class="map-controls" role="toolbar" aria-label="Map controls">
  <button 
    id="zoom-to-route" 
    class="map-control-btn"
    aria-label="Zoom to show entire route"
    title="Zoom to route">
    <svg>...</svg>
  </button>
  <button 
    id="fullscreen-toggle"
    class="map-control-btn"
    aria-label="Toggle fullscreen mode"
    title="Fullscreen">
    <svg>...</svg>
  </button>
</div>
```

### User Experience Enhancements

#### 1. **Route Animation**
- **Progressive Route Drawing**: Animate route polyline drawing
- **Marker Entrance**: Fade-in and scale animations for markers
- **Smooth Zoom**: Animated zoom to route bounds

```javascript
// Animated route drawing
function animateRoute(routeLayer, map) {
  const coordinates = routeLayer.getLatLngs()[0];
  const polyline = L.polyline([], {
    color: '#15803d',
    weight: 4,
    opacity: 0.8
  }).addTo(map);
  
  let index = 0;
  const interval = setInterval(() => {
    if (index < coordinates.length) {
      polyline.addLatLng(coordinates[index]);
      index++;
    } else {
      clearInterval(interval);
      // Replace animated polyline with full route
      map.removeLayer(polyline);
      routeLayer.addTo(map);
    }
  }, 50);
}
```

#### 2. **Route Statistics Display**
- **Visual Metrics**: 
  - Distance with unit toggle (km/miles)
  - Estimated delivery time with traffic consideration
  - Delivery fee breakdown
- **Route Quality Indicators**: 
  - Fastest route badge
  - Shortest route badge
  - Eco-friendly route option

```html
<div class="route-stats grid grid-cols-3 gap-4 mt-4">
  <div class="bg-green-50 rounded-lg p-3 text-center border border-green-200">
    <div class="text-2xl font-bold text-green-700" id="route-distance">12.5 km</div>
    <div class="text-xs text-green-600 mt-1">Distance</div>
  </div>
  <div class="bg-orange-50 rounded-lg p-3 text-center border border-orange-200">
    <div class="text-2xl font-bold text-orange-700" id="route-duration">25 min</div>
    <div class="text-xs text-orange-600 mt-1">Est. Time</div>
  </div>
  <div class="bg-blue-50 rounded-lg p-3 text-center border border-blue-200">
    <div class="text-2xl font-bold text-blue-700" id="delivery-fee">₱150</div>
    <div class="text-xs text-blue-600 mt-1">Delivery Fee</div>
  </div>
</div>
```

#### 3. **Map Customization Options**
- **Map Style Toggle**: Switch between standard and satellite view
- **Layer Controls**: Toggle traffic layer, terrain view
- **Marker Clustering**: For multiple delivery addresses

```javascript
// Map style toggle
const mapStyles = {
  standard: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '© Esri'
  })
};

function toggleMapStyle(style) {
  map.eachLayer(layer => {
    if (layer instanceof L.TileLayer) {
      map.removeLayer(layer);
    }
  });
  mapStyles[style].addTo(map);
}
```

### Performance Metrics

#### Optimization Checklist
- [ ] Map loads in < 2 seconds
- [ ] Route calculation completes in < 3 seconds
- [ ] Smooth 60fps animations
- [ ] Mobile-friendly touch interactions
- [ ] Offline fallback for cached routes
- [ ] Lazy loading for map tiles
- [ ] Debounced API requests
- [ ] Route result caching (localStorage)
- [ ] Progressive image loading
- [ ] Minimized JavaScript bundle size

### Visual Design Consistency

#### Color Scheme Alignment
- **Primary Green**: `#15803d` (FarmIT brand color) for farm markers and routes
- **Accent Orange**: `#f97316` (FarmIT accent) for delivery address markers
- **Background**: Match FarmIT's gradient theme (yellow to green)
- **Text**: Consistent with FarmIT typography

#### Component Styling
- **Rounded Corners**: `rounded-xl` (12px) for map container
- **Shadows**: `shadow-lg` for depth and elevation
- **Backdrop Blur**: `backdrop-blur-sm` for modern glass effect
- **Border**: `border border-gray-200` for subtle definition

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

### Core Functionality
- [ ] OpenRouteService API key configured
- [ ] Route API endpoint returns GeoJSON
- [ ] Map displays with Leaflet
- [ ] Route polyline shows on map
- [ ] Markers display correctly (farm = green, address = orange)
- [ ] Map bounds fit route properly
- [ ] Fallback to straight line if API fails
- [ ] Distance calculation uses route distance (not Haversine)
- [ ] ETA calculation updated based on route
- [ ] Error handling for missing coordinates
- [ ] Rate limiting respected (2K requests/day)

### UI/UX Testing
- [ ] Loading spinner displays while route is fetched
- [ ] Route animation works smoothly
- [ ] Markers have proper tooltips/popups
- [ ] Route info panel displays correctly
- [ ] Error messages are user-friendly
- [ ] Mobile responsive design works on all screen sizes
- [ ] Touch interactions work on mobile devices
- [ ] Map controls (zoom, fullscreen) function properly
- [ ] Keyboard navigation works for accessibility
- [ ] Screen reader announces route information correctly
- [ ] Route statistics display accurate data
- [ ] Color scheme matches FarmIT branding

### Performance Testing
- [ ] Map loads in < 2 seconds
- [ ] Route calculation completes in < 3 seconds
- [ ] Smooth animations (60fps)
- [ ] Route caching works (localStorage)
- [ ] No memory leaks on repeated route requests
- [ ] Mobile performance is acceptable (< 3s load time)
- [ ] Offline fallback works correctly

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
4. **Implement UI improvements** (2-3 hours)
   - Loading states and animations
   - Route info panel
   - Error handling UI
   - Mobile optimizations
5. **Test and debug** (1-2 hours)
6. **Deploy to Vercel** (30 minutes)

**Total Estimated Time:** 7-11 hours (including UI improvements)

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

