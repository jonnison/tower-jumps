# Tower Jumps Frontend

A modern React frontend built with Vite, TypeScript, and Mantine UI for the Tower Jumps Challenge application.

## 🚀 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Mantine 7** - UI component library
- **React Router** - Client-side routing
- **Tabler Icons** - Icon library

## 🏃‍♂️ Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Development

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Open browser**
   Navigate to `http://localhost:5173`

### Docker Development

```bash
# Build and run with docker-compose
docker-compose up frontend

# Or run the entire stack
docker-compose up
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Subscribers.tsx
│   │   └── Map.tsx
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies and scripts
```

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🎨 Features

- **Responsive Design** - Works on desktop and mobile
- **Modern UI** - Clean and intuitive interface with Mantine
- **Type Safety** - Full TypeScript support
- **Fast Development** - Hot module replacement with Vite
- **Component Library** - Rich set of UI components from Mantine

## 🔗 API Integration

The frontend is configured to connect to the Django backend API:
- Development API: `http://localhost:8000`
- Proxy configuration in `vite.config.ts` handles API requests

## 📄 Pages

- **Dashboard** - Overview with statistics and metrics
- **Subscribers** - Manage subscriber data and view details
- **Map** - Interactive map view (placeholder for future implementation)

## 🚀 Deployment

```bash
# Build for production
npm run build

# The built files will be in the `dist/` directory
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request
