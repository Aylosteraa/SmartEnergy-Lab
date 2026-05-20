import { useEffect, useState } from "react";

import MainLayout from "../layouts/MainLayout";

import {
  Card,
  Row,
  Col,
  Spinner,
  Alert,
  Table,
  Badge,
} from "react-bootstrap";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface Forecast24hItem {
  time: string;
  total_consumption: number;
  solar_consumption: number;
  battery_consumption: number;
  solar_generation: number;
}

interface Forecast7dItem {
  date: string;
  total_consumption: number;
  solar_consumption: number;
  battery_consumption: number;
  solar_generation: number;
}

const ForecastPage = () => {
  const [forecast24h, setForecast24h] = useState<
    Forecast24hItem[]
  >([]);

  const [forecast7d, setForecast7d] = useState<
    Forecast7dItem[]
  >([]);

  const [forecastMonth, setForecastMonth] = useState<
    Forecast7dItem[]
  >([]);

  const [recommendations, setRecommendations] =
    useState<string[]>([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  useEffect(() => {
    loadForecastData();
  }, []);

  const loadForecastData = async () => {
    try {
      setLoading(true);

      const [
        forecast24hRes,
        forecast7dRes,
        forecastMonthRes,
        recommendationsRes,
      ] = await Promise.all([
        fetch("http://localhost:8000/forecast/24h"),
        fetch("http://localhost:8000/forecast/7d"),
        fetch("http://localhost:8000/forecast/month"),
        fetch(
          "http://localhost:8000/forecast/recommendations"
        ),
      ]);

      const forecast24hData =
        await forecast24hRes.json();

      const forecast7dData =
        await forecast7dRes.json();

      const forecastMonthData =
        await forecastMonthRes.json();

      const recommendationsData =
        await recommendationsRes.json();

      setForecast24h(forecast24hData);

      setForecast7d(forecast7dData);

      setForecastMonth(forecastMonthData);

      setRecommendations(recommendationsData);
    } catch (err) {
      setError(
        "Не вдалося завантажити прогноз."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================
  // SUMMARY CARDS
  // =========================================

  const tomorrowConsumption =
    forecast24h.reduce(
      (sum, item) =>
        sum + item.total_consumption,
      0
    );

  const tomorrowSolar =
    forecast24h.reduce(
      (sum, item) =>
        sum + item.solar_generation,
      0
    );

  const batteryUsage =
    forecast24h.reduce(
      (sum, item) =>
        sum + item.battery_consumption,
      0
    );

  // =========================================
  // LOADING
  // =========================================

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <Spinner animation="border" />
      </div>
    );
  }

  // =========================================
  // ERROR
  // =========================================

  if (error) {
    return (
      <div className="container mt-4">
        <Alert variant="danger">
          {error}
        </Alert>
      </div>
    );
  }

  return (
    <MainLayout>
    <div className="container-fluid p-4 bg-light min-vh-100">

      {/* ================================= */}
      {/* PAGE TITLE */}
      {/* ================================= */}

      <div className="mb-4">
        <h1 className="fw-bold">
          Прогнозування енергоспоживання
        </h1>

        <p className="text-muted">
          Аналітика та AI-прогнозування
          споживання електроенергії
        </p>
      </div>

      {/* ================================= */}
      {/* SUMMARY CARDS */}
      {/* ================================= */}

      <Row className="g-4 mb-4">

        <Col md={4}>
          <Card className="shadow border-0 h-100">
            <Card.Body>
              <h6 className="text-muted">
                Споживання завтра
              </h6>

              <h2 className="fw-bold">
                {tomorrowConsumption.toFixed(2)} kWh
              </h2>
            </Card.Body>
          </Card>
        </Col>

        <Col md={4}>
          <Card className="shadow border-0 h-100">
            <Card.Body>
              <h6 className="text-muted">
                Генерація сонячної енергії
              </h6>

              <h2 className="fw-bold text-warning">
                {tomorrowSolar.toFixed(2)} kWh
              </h2>
            </Card.Body>
          </Card>
        </Col>

        <Col md={4}>
          <Card className="shadow border-0 h-100">
            <Card.Body>
              <h6 className="text-muted">
                Використання батареї
              </h6>

              <h2 className="fw-bold text-success">
                {batteryUsage.toFixed(2)} kWh
              </h2>
            </Card.Body>
          </Card>
        </Col>

      </Row>

      {/* ================================= */}
      {/* 24H CHART */}
      {/* ================================= */}

      <Card className="shadow border-0 mb-4">

        <Card.Body>

          <div className="d-flex justify-content-between align-items-center mb-3">

            <h4 className="fw-bold mb-0">
              Прогноз на 24 години
            </h4>

            <Badge bg="primary">
              AI прогноз
            </Badge>

          </div>

          <ResponsiveContainer
            width="100%"
            height={400}
          >

            <LineChart data={forecast24h}>

              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="time" />

              <YAxis />

              <Tooltip />

              <Legend />

              <Line
                type="monotone"
                dataKey="total_consumption"
                stroke="#0d6efd"
                strokeWidth={3}
                name="Загальне споживання"
              />

              <Line
                type="monotone"
                dataKey="solar_generation"
                stroke="#ffc107"
                strokeWidth={3}
                name="Сонячна генерація"
              />

              <Line
                type="monotone"
                dataKey="battery_consumption"
                stroke="#198754"
                strokeWidth={3}
                name="Батарея"
              />

            </LineChart>

          </ResponsiveContainer>

        </Card.Body>

      </Card>

      {/* ================================= */}
      {/* 7 DAYS CHART */}
      {/* ================================= */}

      <Card className="shadow border-0 mb-4">

        <Card.Body>

          <h4 className="fw-bold mb-4">
            Прогноз на 7 днів
          </h4>

          <ResponsiveContainer
            width="100%"
            height={400}
          >

            <LineChart data={forecast7d}>

              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="date" />

              <YAxis />

              <Tooltip />

              <Legend />

              <Line
                type="monotone"
                dataKey="total_consumption"
                stroke="#0d6efd"
                strokeWidth={3}
                name="Споживання"
              />

              <Line
                type="monotone"
                dataKey="solar_generation"
                stroke="#ffc107"
                strokeWidth={3}
                name="Генерація"
              />

            </LineChart>

          </ResponsiveContainer>

        </Card.Body>

      </Card>

      {/* ================================= */}
      {/* MONTH TABLE */}
      {/* ================================= */}

      <Card className="shadow border-0 mb-4">

        <Card.Body>

          <h4 className="fw-bold mb-4">
            Місячний прогноз
          </h4>

          <div className="table-responsive">

            <Table
              striped
              bordered
              hover
              className="align-middle"
            >

              <thead>

                <tr>
                  <th>Дата</th>
                  <th>Загальне</th>
                  <th>Сонячна</th>
                  <th>Батарея</th>
                  <th>Генерація</th>
                </tr>

              </thead>

              <tbody>

                {forecastMonth.map(
                  (item, index) => (
                    <tr key={index}>

                      <td>{item.date}</td>

                      <td>
                        {
                          item.total_consumption
                        }{" "}
                        kWh
                      </td>

                      <td>
                        {
                          item.solar_consumption
                        }{" "}
                        kWh
                      </td>

                      <td>
                        {
                          item.battery_consumption
                        }{" "}
                        kWh
                      </td>

                      <td>
                        {
                          item.solar_generation
                        }{" "}
                        kWh
                      </td>

                    </tr>
                  )
                )}

              </tbody>

            </Table>

          </div>

        </Card.Body>

      </Card>

      {/* ================================= */}
      {/* RECOMMENDATIONS */}
      {/* ================================= */}

      <Card className="shadow border-0">

        <Card.Body>

          <h4 className="fw-bold mb-4">
            AI рекомендації
          </h4>

          <Row className="g-3">

            {recommendations.map(
              (item, index) => (
                <Col
                  md={4}
                  key={index}
                >
                  <Card className="border-0 bg-primary bg-opacity-10 h-100">

                    <Card.Body>

                      <h6 className="fw-bold text-primary">
                        Рекомендація
                      </h6>

                      <p className="mb-0">
                        {item}
                      </p>

                    </Card.Body>

                  </Card>
                </Col>
              )
            )}

          </Row>

        </Card.Body>

      </Card>

    </div>
    </MainLayout>
  );
};

export default ForecastPage;