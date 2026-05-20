import { createBrowserRouter } from "react-router-dom";
import RealtimePage from "../pages/RealtimePage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import ProfilePage from "../pages/ProfilePage";
import AnalyticsPage from "../pages/AnalyticsPage";
import HistoryPage from "../pages/HistoryPage";
import RecommendationPage from "../pages/RecommendationsPage";
import SolarPage from "../pages/SolarPage"
import ForecastPage from "../pages/ForecastPage";

export const router = createBrowserRouter([
  
  {
    path: "/login",
    element: <LoginPage />,
  },

  {
    path: "/register",
    element: <RegisterPage />,
  }, 

  {
    path: "/profile",
    element: <ProfilePage />,
  },

  {
    path: "/analytics",
    element: <AnalyticsPage />,
  },

  {
    path: "/history",
    element: <HistoryPage />,
  },

  {
    path: "/recommendations",
    element: <RecommendationPage />,
  },

  {
    path: "/solar",
    element: <SolarPage />,
  },

  {
    path: "/forecast",
    element: <ForecastPage />,
  },

  {
    path: "/",
    element: <RealtimePage />,
  }

]);