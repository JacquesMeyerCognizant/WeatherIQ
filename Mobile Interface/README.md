# Cognizant Weather IQ

A professional mobile interface for weather prediction designed specifically for offshore windfarm engineers. This application provides an intuitive way to input forecast parameters and access weather predictions powered by GenCast technology.

## Overview

Cognizant Weather IQ is a clean, modern mobile application interface that allows offshore windfarm engineers to:
- Select current and target dates for weather forecasting
- Choose specific windfarms from a predefined list
- Input the number of operational turbines
- Access forecast videos and downloadable reports

## Features

### Core Functionality
- **Date Selection**: Auto-filled current date with interactive calendar picker for target dates
- **Windfarm Selection**: Dropdown menu with predefined offshore windfarm locations
- **Turbine Management**: Numeric input for operational turbine count (1-500)
- **Forecast Access**: Buttons for viewing video forecasts and downloading reports
- **Form Validation**: Buttons are disabled until all required fields are completed

### Design Features
- **Mobile-First**: Optimized for mobile screens with touch-friendly interactions
- **Professional Aesthetic**: Clean blue/grey/white color palette reflecting weather and technology themes
- **Responsive Layout**: Proper spacing and responsive design considerations
- **Branded**: Integrated Cognizant Weather IQ logo
- **Accessible**: Clear visual hierarchy and accessible form controls

## Technical Stack

- **Frontend Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: ShadCN UI component library
- **Icons**: Lucide React
- **Date Handling**: Native JavaScript Date API with custom formatting
- **State Management**: React useState hooks

## Project Structure

```
├── App.tsx                          # Main application entry point
├── components/
│   ├── WeatherIQInterface.tsx       # Main interface component
│   ├── figma/
│   │   └── ImageWithFallback.tsx    # Image component with fallback
│   └── ui/                          # ShadCN UI components
│       ├── button.tsx               # Custom button with forwardRef
│       ├── calendar.tsx             # Calendar picker component
│       ├── card.tsx                 # Card layout component
│       ├── input.tsx                # Form input component
│       ├── label.tsx                # Form label component
│       ├── popover.tsx              # Popover container
│       ├── select.tsx               # Dropdown select component
│       └── ...                      # Other UI components
├── styles/
│   └── globals.css                  # Global CSS with Tailwind v4 config
└── guidelines/
    └── Guidelines.md                # Development guidelines
```

## Code Documentation

### Main Components

#### `App.tsx`
The application entry point that renders the main WeatherIQInterface component.

#### `WeatherIQInterface.tsx`
The primary component containing all application logic and UI. Key features:

**State Management:**
- `currentDate`: Auto-set to current date (July 28, 2025)
- `targetDate`: User-selected forecast target date
- `selectedWindfarm`: Chosen windfarm from dropdown
- `turbineCount`: Number of operational turbines

**Key Functions:**
- `formatDate()`: Formats dates in readable format (e.g., "Monday, July 28, 2025")

**Validation:**
- Action buttons are disabled when required fields are empty
- Target date picker prevents selection of past dates
- Turbine count input accepts values between 1-500

### UI Components

All UI components are based on ShadCN UI library with custom styling:

- **Button**: Enhanced with React.forwardRef for proper ref handling
- **Card**: Main container with semi-transparent background and backdrop blur
- **Calendar**: Date picker with disabled past dates
- **Input**: Form inputs with consistent styling
- **Select**: Dropdown menus with custom styling
- **Popover**: Container for calendar picker

### Styling System

The application uses Tailwind CSS v4 with a custom design system:

**Color Palette:**
- Primary blues: `blue-50`, `blue-600`, `blue-700`
- Neutral grays: `slate-100`, `slate-600`, `slate-700`, `slate-800`
- Background: Gradient from `blue-50` to `slate-100`

**Typography:**
- Base font size: 14px
- Consistent font weights and line heights
- Custom typography tokens defined in globals.css

## Setup and Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager
- Modern web browser with ES2022 support

### Installation Steps

1. **Clone/Download the project files**
   ```bash
   # If using git
   git clone <repository-url>
   cd cognizant-weather-iq
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open in browser**
   Navigate to `http://localhost:3000` (or the port shown in terminal)

### Production Build

To create a production build:

```bash
npm run build
# or
yarn build
```

## Usage Instructions

### Basic Workflow

1. **View Current Date**: The current date is automatically displayed and cannot be modified
2. **Select Target Date**: Click the "Select target date" button to open the calendar picker
3. **Choose Windfarm**: Use the dropdown to select from available offshore windfarms:
   - North Sea Alpha
   - Baltic Beta
   - Atlantic Gamma
   - Irish Sea Delta
   - North Sea Epsilon
   - Celtic Zeta
4. **Enter Turbine Count**: Input the number of operational turbines (1-500)
5. **Access Forecasts**: Once all fields are completed:
   - Click "View Forecast Video" to watch weather predictions
   - Click "Download Forecast" to get downloadable reports

### Form Validation

- All fields must be completed before action buttons are enabled
- Target date cannot be earlier than the current date
- Turbine count must be between 1 and 500

## Development Notes

### Key Dependencies

- **React**: Frontend framework with hooks for state management
- **TypeScript**: Type safety and better development experience
- **Tailwind CSS v4**: Utility-first CSS framework with custom design tokens
- **ShadCN UI**: Pre-built accessible component library
- **Lucide React**: Icon library for consistent iconography

### Customizations Made

1. **Button Component**: Added React.forwardRef to fix ref forwarding issues with Radix UI
2. **Date Formatting**: Custom date formatting function for consistent display
3. **Validation Logic**: Form validation that enables/disables action buttons
4. **Responsive Design**: Mobile-first approach with proper touch targets
5. **Brand Integration**: Custom logo integration with proper sizing

### Future Enhancement Opportunities

- **API Integration**: Connect to real weather prediction services
- **Video Streaming**: Implement actual forecast video playback
- **Data Persistence**: Add local storage or backend integration
- **Offline Support**: Progressive Web App (PWA) capabilities
- **Multi-language Support**: Internationalization for global use
- **Advanced Analytics**: Usage tracking and performance monitoring

## Troubleshooting

### Common Issues

1. **Ref Forwarding Warnings**: Fixed in current version with forwardRef implementation
2. **Date Picker Not Opening**: Ensure all ShadCN UI dependencies are properly installed
3. **Styling Issues**: Verify Tailwind CSS v4 is properly configured in globals.css

### Browser Compatibility

- Modern browsers with ES2022 support
- Mobile browsers (iOS Safari 14+, Chrome Mobile 90+)
- Desktop browsers (Chrome 90+, Firefox 88+, Safari 14+)

## License

This project is proprietary software developed for Cognizant Weather IQ.

## Support

For technical support or questions about the interface, please contact the development team.

---

**Powered by GenCast** - Advanced weather prediction technology for offshore wind energy.