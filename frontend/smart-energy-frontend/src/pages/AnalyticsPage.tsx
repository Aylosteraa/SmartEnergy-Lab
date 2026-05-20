import MainLayout from "../layouts/MainLayout";

import {
  useEffect,
  useState
} from "react";

import {
  Row,
  Col,
  Card,
  Button,
  ButtonGroup
} from "react-bootstrap";

import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

import API from "../api/api";

import { getActiveCard }
from "../utils/activeCard";


function AnalyticsPage() {

  const [period, setPeriod] =
    useState("week");

  const [type, setType] =
    useState("total");

  const [data, setData] =
    useState([]);

  const [stats, setStats] =
    useState({
      avg: 0,
      min: 0,
      max: 0
    });

  const loadAnalytics = async () => {

    try {

      const cardId =
        getActiveCard();

      const response = await API.get(
        "/analytics",
        {
          params: {
            card_id: cardId,
            period,
            analytics_type: type
          }
        }
      );

      setData(response.data.chart);

      setStats(response.data.stats);

    } catch (error) {

      console.error(error);
    }
  };


  useEffect(() => {

    loadAnalytics();

  }, [period, type]);


  return (
    <MainLayout>
    <div className="container-fluid">

      {/* HEADER */}
      <div className="mb-4">

        <h2 className="fw-bold">
          Аналітика
        </h2>

        <p className="text-muted">

          Аналіз енергоспоживання

        </p>

      </div>


      {/* FILTERS */}
      <Row className="g-3 mb-4">

        <Col lg={6}>

          <Card className="border-0 shadow-sm rounded-4 p-3">

            <ButtonGroup>

              <Button
                variant={
                  period === "week"
                    ? "dark"
                    : "outline-dark"
                }

                onClick={() =>
                  setPeriod("week")
                }
              >

                Тиждень

              </Button>

              <Button
                variant={
                  period === "month"
                    ? "dark"
                    : "outline-dark"
                }

                onClick={() =>
                  setPeriod("month")
                }
              >

                Місяць

              </Button>

              <Button
                variant={
                  period === "year"
                    ? "dark"
                    : "outline-dark"
                }

                onClick={() =>
                  setPeriod("year")
                }
              >

                Рік

              </Button>

            </ButtonGroup>

          </Card>

        </Col>


        <Col lg={6}>

          <Card className="border-0 shadow-sm rounded-4 p-3">

            <ButtonGroup className="flex-wrap">

              <Button
                variant={
                  type === "total"
                    ? "dark"
                    : "outline-dark"
                }

                onClick={() =>
                  setType("total")
                }
              >

                Загальне

              </Button>

              <Button
                variant={
                  type === "solar"
                    ? "dark"
                    : "outline-dark"
                }

                onClick={() =>
                  setType("solar")
                }
              >

                Сонце

              </Button>

              <Button
                variant={
                  type === "battery"
                    ? "dark"
                    : "outline-dark"
                }

                onClick={() =>
                  setType("battery")
                }
              >

                Батарея

              </Button>

              <Button
                variant={
                  type === "generation"
                    ? "dark"
                    : "outline-dark"
                }

                onClick={() =>
                  setType("generation")
                }
              >

                Генерація

              </Button>

            </ButtonGroup>

          </Card>

        </Col>

      </Row>


      {/* CHART */}
      <Card className="border-0 shadow-sm rounded-4 p-4 mb-4">

        <ResponsiveContainer
          width="100%"
          height={400}
        >

          <LineChart data={data}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="label" />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="value"
              strokeWidth={3}
            />

          </LineChart>

        </ResponsiveContainer>

      </Card>


      {/* DASHBOARDS */}
      <Row className="g-4">

        <Col lg={4}>

          <Card className="border-0 shadow-sm rounded-4 p-4">

            <h6 className="text-muted">
              Середнє
            </h6>

            <h2 className="fw-bold">
              {stats.avg} kWh
            </h2>

          </Card>

        </Col>


        <Col lg={4}>

          <Card className="border-0 shadow-sm rounded-4 p-4">

            <h6 className="text-muted">
              Мінімальне
            </h6>

            <h2 className="fw-bold">
              {stats.min} kWh
            </h2>

          </Card>

        </Col>


        <Col lg={4}>

          <Card className="border-0 shadow-sm rounded-4 p-4">

            <h6 className="text-muted">
              Максимальне
            </h6>

            <h2 className="fw-bold">
              {stats.max} kWh
            </h2>

          </Card>

        </Col>

      </Row>

    </div>
    </MainLayout>
  );
}

export default AnalyticsPage;