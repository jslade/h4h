import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import {
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'

import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

import './index.css';
import reportWebVitals from './reportWebVitals';

import Root from './components/root';
import Raw from './components/asics/raw';
import Login from './pages/Login';
import RequireAuth from './components/RequireAuth';

const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/",
    element: <RequireAuth><Root /></RequireAuth>,
  },
  {
    path: "/asics/raw/:name",
    element: <RequireAuth><Raw /></RequireAuth>
  },
]);

const queryClient = new QueryClient()


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
