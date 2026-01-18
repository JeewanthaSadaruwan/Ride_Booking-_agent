import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Location, Route } from '@/types';
import { cn } from '@/utils/helpers';

// Fix for default marker icons in Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface MapComponentProps {
  pickup: Location | null;
  dropoff: Location | null;
  route: Route | null;
  onPickupMove?: (location: Location) => void;
  onDropoffMove?: (location: Location) => void;
  isPicking?: boolean;
  onMapSelect?: (lat: number, lon: number) => void;
}

export const MapComponent: React.FC<MapComponentProps> = ({
  pickup,
  dropoff,
  route,
  onPickupMove,
  onDropoffMove,
  isPicking,
  onMapSelect,
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const pickupMarkerRef = useRef<L.Marker | null>(null);
  const dropoffMarkerRef = useRef<L.Marker | null>(null);
  const routeLayerRef = useRef<L.Polyline | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const hasMountedRef = useRef(false);

  // Initialize map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current).setView([6.9271, 79.8612], 13); // Colombo
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);
    mapRef.current = map;

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Recreate map on pick mode toggle (prevents blank tiles in some layouts)
  useEffect(() => {
    if (!containerRef.current || !mapRef.current) return;
    if (!hasMountedRef.current) {
      hasMountedRef.current = true;
      return;
    }

    mapRef.current.remove();
    mapRef.current = null;
    pickupMarkerRef.current = null;
    dropoffMarkerRef.current = null;
    routeLayerRef.current = null;

    const map = L.map(containerRef.current).setView([6.9271, 79.8612], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);
    mapRef.current = map;
  }, [isPicking]);

  useEffect(() => {
    if (!mapRef.current || !onMapSelect) return;
    const handleClick = (e: L.LeafletMouseEvent) => {
      onMapSelect(e.latlng.lat, e.latlng.lng);
    };
    mapRef.current.on('click', handleClick);
    return () => {
      mapRef.current?.off('click', handleClick);
    };
  }, [onMapSelect]);

  // Ensure tiles render correctly after layout changes
  useEffect(() => {
    if (!mapRef.current) return;
    const fast = window.setTimeout(() => {
      mapRef.current?.invalidateSize();
    }, 0);
    const slow = window.setTimeout(() => {
      mapRef.current?.invalidateSize();
      const center = mapRef.current?.getCenter();
      const zoom = mapRef.current?.getZoom();
      if (center && typeof zoom === 'number') {
        mapRef.current?.setView(center, zoom, { animate: false });
      }
    }, 150);
    return () => {
      window.clearTimeout(fast);
      window.clearTimeout(slow);
    };
  }, [pickup, dropoff, route, isPicking]);

  // Update pickup marker
  useEffect(() => {
    if (!mapRef.current || !pickup) return;

    // Remove existing marker
    if (pickupMarkerRef.current) {
      pickupMarkerRef.current.remove();
    }

    // Create green icon for pickup
    const pickupIcon = L.icon({
      iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUiIGhlaWdodD0iNDEiIHZpZXdCb3g9IjAgMCAyNSA0MSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIuNSAwQzUuNiAwIDAgNS42IDAgMTIuNWMwIDkuNCAxMi41IDI4LjUgMTIuNSAyOC41UzI1IDIxLjkgMjUgMTIuNUMyNSA1LjYgMTkuNCAwIDEyLjUgMHptMCAxN2MtMi41IDAtNC41LTItNC41LTQuNXMyLTQuNSA0LjUtNC41IDQuNSAyIDQuNSA0LjUtMiA0LjUtNC41IDQuNXoiIGZpbGw9IiMxMGI5ODEiLz48L3N2Zz4=',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [0, -41],
    });

    // Add new marker
    pickupMarkerRef.current = L.marker([pickup.lat, pickup.lon], {
      icon: pickupIcon,
      draggable: !!onPickupMove,
    })
      .addTo(mapRef.current)
      .bindPopup(`<b>Pickup:</b> ${pickup.text}`);

    if (onPickupMove) {
      pickupMarkerRef.current.on('dragend', (e) => {
        const pos = e.target.getLatLng();
        onPickupMove({
          ...pickup,
          lat: pos.lat,
          lon: pos.lng,
        });
      });
    }
  }, [pickup, onPickupMove, isPicking]);

  // Update dropoff marker
  useEffect(() => {
    if (!mapRef.current || !dropoff) return;

    // Remove existing marker
    if (dropoffMarkerRef.current) {
      dropoffMarkerRef.current.remove();
    }

    // Create red icon for dropoff
    const dropoffIcon = L.icon({
      iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUiIGhlaWdodD0iNDEiIHZpZXdCb3g9IjAgMCAyNSA0MSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIuNSAwQzUuNiAwIDAgNS42IDAgMTIuNWMwIDkuNCAxMi41IDI4LjUgMTIuNSAyOC41UzI1IDIxLjkgMjUgMTIuNUMyNSA1LjYgMTkuNCAwIDEyLjUgMHptMCAxN2MtMi41IDAtNC41LTItNC41LTQuNXMyLTQuNSA0LjUtNC41IDQuNSAyIDQuNSA0LjUtMiA0LjUtNC41IDQuNXoiIGZpbGw9IiNlZjQ0NDQiLz48L3N2Zz4=',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [0, -41],
    });

    // Add new marker
    dropoffMarkerRef.current = L.marker([dropoff.lat, dropoff.lon], {
      icon: dropoffIcon,
      draggable: !!onDropoffMove,
    })
      .addTo(mapRef.current)
      .bindPopup(`<b>Dropoff:</b> ${dropoff.text}`);

    if (onDropoffMove) {
      dropoffMarkerRef.current.on('dragend', (e) => {
        const pos = e.target.getLatLng();
        onDropoffMove({
          ...dropoff,
          lat: pos.lat,
          lon: pos.lng,
        });
      });
    }
  }, [dropoff, onDropoffMove, isPicking]);

  // Update route
  useEffect(() => {
    if (!mapRef.current) return;

    // Remove existing route
    if (routeLayerRef.current) {
      routeLayerRef.current.remove();
    }

    if (route && route.polyline && route.polyline.length > 0) {
      // Add route polyline
      routeLayerRef.current = L.polyline(route.polyline, {
        color: '#0ea5e9',
        weight: 4,
        opacity: 0.7,
      }).addTo(mapRef.current);

      // Fit bounds to show entire route
      const bounds = L.latLngBounds([]);
      if (pickup) bounds.extend([pickup.lat, pickup.lon]);
      if (dropoff) bounds.extend([dropoff.lat, dropoff.lon]);
      mapRef.current.fitBounds(bounds, { padding: [50, 50] });
    } else if (pickup && dropoff) {
      // If no route polyline, just fit to markers
      const bounds = L.latLngBounds([
        [pickup.lat, pickup.lon],
        [dropoff.lat, dropoff.lon],
      ]);
      mapRef.current.fitBounds(bounds, { padding: [50, 50] });
    } else if (pickup) {
      mapRef.current.setView([pickup.lat, pickup.lon], 13);
    } else if (dropoff) {
      mapRef.current.setView([dropoff.lat, dropoff.lon], 13);
    }
  }, [route, pickup, dropoff, isPicking]);

  return (
    <div className="w-full h-full rounded-lg overflow-hidden shadow-lg">
      <div
        ref={containerRef}
        className={cn('w-full h-full', isPicking ? 'cursor-crosshair' : '')}
      />
    </div>
  );
};
