# Ride Booking Agent - React Frontend

Modern, production-ready React frontend for the Conversational Vehicle Booking Agent.

## 🚀 Features

- **Modern UI/UX**: Clean, responsive interface comparable to Uber/Bolt
- **Real-time Chat**: AI-powered conversational booking flow
- **Interactive Maps**: Leaflet integration with OpenStreetMap
- **Vehicle Selection**: Dynamic vehicle recommendations with pricing
- **Booking Management**: View and manage all your bookings
- **Authentication**: Secure JWT-based authentication
- **Type Safety**: Full TypeScript implementation
- **State Management**: Zustand for global state
- **API Integration**: React Query for efficient data fetching

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Query (TanStack Query)** - Server state management
- **Zustand** - Client state management
- **React Router** - Navigation
- **Leaflet** - Maps
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

## 📁 Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   ├── Modal.tsx
│   ├── Loader.tsx
│   ├── StatusBadge.tsx
│   ├── Sidebar.tsx
│   ├── Layout.tsx
│   ├── ChatMessage.tsx
│   ├── ChatInput.tsx
│   ├── ChatContainer.tsx
│   ├── MapComponent.tsx
│   ├── VehicleCard.tsx
│   ├── BookingConfirmationModal.tsx
│   └── ProtectedRoute.tsx
├── pages/           # Page components
│   ├── LoginPage.tsx
│   ├── SignupPage.tsx
│   ├── BookRidePage.tsx
│   └── MyBookingsPage.tsx
├── services/        # API services
│   ├── api.ts
│   ├── authService.ts
│   ├── chatService.ts
│   ├── bookingService.ts
│   └── locationService.ts
├── store/           # Zustand stores
│   ├── authStore.ts
│   └── bookingStore.ts
├── types/           # TypeScript types
│   └── index.ts
├── hooks/           # Custom React hooks
│   └── useHooks.ts
├── utils/           # Utility functions
│   └── helpers.ts
├── App.tsx          # Main app component
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## 🔧 Configuration

### Backend API Proxy

The frontend is configured to proxy API requests to the backend. Update `vite.config.ts` if your backend runs on a different port:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000', // Change this if needed
      changeOrigin: true,
    },
  },
}
```

### Environment Variables

Create a `.env` file if you need to customize settings:

```env
VITE_API_URL=http://localhost:8000
```

## 📱 Features Walkthrough

### 1. Authentication Flow
- **Login**: Existing users sign in with email/password
- **Signup**: New users create account with name, email, phone, password
- **Protected Routes**: Unauthenticated users redirected to login

### 2. Sidebar
- User profile card with name, email, phone
- Stats: Total bookings, completed trips, total spent
- "Start New Trip" button to reset booking flow
- Feature list and version info

### 3. Book a Ride Tab
- **Chat Interface**: 
  - Natural language conversation with AI agent
  - User messages on right, agent on left
  - System notifications for detected locations and routes
  - Auto-scroll to latest message
  - Typing indicator when agent is responding

- **Map Integration**:
  - Shows pickup marker (green)
  - Shows dropoff marker (red)
  - Displays route polyline
  - Auto-fits to show entire route

- **Vehicle Selection**:
  - Cards showing vehicle type, capacity, features
  - Estimated price and ETA
  - Visual selection with highlighting

- **Booking Confirmation**:
  - Modal with trip summary
  - Displays all details before confirmation
  - Creates booking on confirmation

### 4. My Bookings Tab
- List of all user bookings
- Status badges (Confirmed, Completed, Cancelled, Pending)
- Expandable cards showing full details
- Cancel booking action (for confirmed/pending)
- Shows driver details when available

## 🎨 Styling

The app uses Tailwind CSS with a custom theme:

- **Primary Color**: Blue (`primary-*` classes)
- **Responsive**: Mobile-first design
- **Animations**: Smooth transitions and loading states
- **Custom Scrollbars**: Styled for better UX

## 🔒 Authentication

- JWT tokens stored in `localStorage`
- Axios interceptor adds token to all requests
- Automatic redirect to login on 401 errors
- Protected routes using `ProtectedRoute` component

## 📡 API Integration

All API calls are handled through service files:

- `authService`: Login, signup, profile
- `chatService`: Send messages, get history
- `bookingService`: Create, list, cancel bookings
- `locationService`: Geocoding, route calculation
- `vehicleService`: Get vehicles, recommendations

React Query is used for:
- Automatic caching
- Background refetching
- Optimistic updates
- Loading/error states

## 🧪 Development Tips

### Add New API Endpoint

1. Add type definition in `types/index.ts`
2. Add service method in appropriate service file
3. Use with React Query:

```typescript
const { data, isLoading } = useQuery({
  queryKey: ['key'],
  queryFn: serviceMethod,
});
```

### Add New Component

1. Create in `components/` directory
2. Export from component file
3. Import where needed

### State Management

- **Global state**: Use Zustand stores (`authStore`, `bookingStore`)
- **Server state**: Use React Query
- **Local state**: Use React `useState`

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Build errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API not connecting
- Check backend is running on port 8000
- Check proxy configuration in `vite.config.ts`
- Check browser console for errors

## 🚀 Deployment

### Deploy to Vercel/Netlify

1. Build the project:
```bash
npm run build
```

2. Deploy the `dist/` directory

3. Set up environment variables in your hosting platform

4. Configure API proxy or update API URL

## 📄 License

This project is part of the Ride Booking Agent system.

## 🤝 Contributing

1. Follow the existing code structure
2. Use TypeScript for all new files
3. Follow Tailwind CSS conventions
4. Add comments for complex logic
5. Test thoroughly before committing

## 📞 Support

For issues or questions, please refer to the main project documentation.
