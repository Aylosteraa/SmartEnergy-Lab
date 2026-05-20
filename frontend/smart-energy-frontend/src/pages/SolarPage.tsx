import MainLayout from "../layouts/MainLayout";

import {
  Sun,
  BatteryCharging,
  LightningCharge,
  ThermometerHalf,
  Cpu,
  Activity
} from "react-bootstrap-icons";

function SolarPage() {

  return (

    <MainLayout>

      {/* Title */}
      <div className="mb-4">

        <h2 className="fw-bold">
          Стан сонячної системи
        </h2>

        <p className="text-muted">
          Моніторинг сонячних панелей та акумуляторної системи
        </p>

      </div>

      {/* Top Cards */}
      <div className="row g-4 mb-4">

        {/* Generation */}
        <div className="col-lg-6">

          <div
            className="card border-0 shadow-sm rounded-4 p-4 h-100"
            style={{ minHeight: "250px" }}
          >

            <div className="d-flex justify-content-between align-items-center mb-4">

              <h4 className="fw-bold mb-0">
                Генерація енергії
              </h4>

              <Sun
                size={34}
                className="text-warning"
              />

            </div>

            <h1 className="fw-bold">
              5.6 кВт
            </h1>

            <p className="text-muted mt-3 mb-0">
              Поточна генерація сонячної енергії
            </p>

          </div>

        </div>

        {/* Battery */}
        <div className="col-lg-6">

          <div
            className="card border-0 shadow-sm rounded-4 p-4 h-100"
            style={{ minHeight: "250px" }}
          >

            <div className="d-flex justify-content-between align-items-center mb-4">

              <h4 className="fw-bold mb-0">
                Заряд акумулятора
              </h4>

              <BatteryCharging
                size={34}
                className="text-success"
              />

            </div>

            <h1 className="fw-bold">
              76%
            </h1>

            <p className="text-muted mt-3 mb-0">
              Поточний рівень заряду акумулятора
            </p>

          </div>

        </div>

      </div>

      {/* Middle Cards */}
      <div className="row g-4 mb-4">

        {/* Voltage */}
        <div className="col-lg-6">

          <div
            className="card border-0 shadow-sm rounded-4 p-4 h-100"
            style={{ minHeight: "250px" }}
          >

            <div className="d-flex justify-content-between align-items-center mb-4">

              <h4 className="fw-bold mb-0">
                Напруга системи
              </h4>

              <LightningCharge
                size={34}
                className="text-primary"
              />

            </div>

            <h1 className="fw-bold">
              228 В
            </h1>

            <p className="text-muted mt-3 mb-0">
              Поточна напруга енергосистеми
            </p>

          </div>

        </div>

        {/* Temperature */}
        <div className="col-lg-6">

          <div
            className="card border-0 shadow-sm rounded-4 p-4 h-100"
            style={{ minHeight: "250px" }}
          >

            <div className="d-flex justify-content-between align-items-center mb-4">

              <h4 className="fw-bold mb-0">
                Температура панелей
              </h4>

              <ThermometerHalf
                size={34}
                className="text-danger"
              />

            </div>

            <h1 className="fw-bold">
              34°C
            </h1>

            <p className="text-muted mt-3 mb-0">
              Температура поверхні сонячних панелей
            </p>

          </div>

        </div>

      </div>

      {/* Bottom Section */}
      <div className="row g-4">

        {/* Inverter + Solar Status */}
        <div className="col-lg-6">

          <div
            className="card border-0 shadow-sm rounded-4 p-4 h-100"
          >

            <div className="d-flex align-items-center gap-3 mb-4">

              <Cpu
                size={28}
                className="text-dark"
              />

              <h4 className="fw-bold mb-0">
                Стан обладнання
              </h4>

            </div>

            <div className="d-flex flex-column gap-3">

              <div className="bg-light rounded-4 p-4">

                <p className="text-muted mb-2">
                  Стан інвертора
                </p>

                <h5 className="fw-bold text-success">
                  Активний
                </h5>

              </div>

              <div className="bg-light rounded-4 p-4">

                <p className="text-muted mb-2">
                  Стан акумулятора
                </p>

                <h5 className="fw-bold text-success">
                  Стабільний
                </h5>

              </div>

              <div className="bg-light rounded-4 p-4">

                <p className="text-muted mb-2">
                  Ефективність панелей
                </p>

                <h5 className="fw-bold">
                  87%
                </h5>

              </div>

            </div>

          </div>

        </div>

        {/* Live Solar Events */}
        <div className="col-lg-6">

          <div
            className="card border-0 shadow-sm rounded-4 p-4 h-100"
          >

            <div className="d-flex align-items-center gap-3 mb-4">

              <Activity
                size={28}
                className="text-warning"
              />

              <h4 className="fw-bold mb-0">
                Події системи
              </h4>

            </div>

            <div className="d-flex flex-column gap-3">

              <div className="bg-light rounded-4 p-3">

                <div className="d-flex justify-content-between">

                  <div>

                    <p className="fw-semibold mb-1">
                      Висока генерація енергії
                    </p>

                    <small className="text-muted">
                      Система працює з максимальною ефективністю
                    </small>

                  </div>

                  <small className="text-muted">
                    14:28
                  </small>

                </div>

              </div>

              <div className="bg-light rounded-4 p-3">

                <div className="d-flex justify-content-between">

                  <div>

                    <p className="fw-semibold mb-1">
                      Акумулятор перейшов у режим зарядки
                    </p>

                    <small className="text-muted">
                      Надлишок енергії направлено в систему накопичення
                    </small>

                  </div>

                  <small className="text-muted">
                    13:54
                  </small>

                </div>

              </div>

              <div className="bg-light rounded-4 p-3">

                <div className="d-flex justify-content-between">

                  <div>

                    <p className="fw-semibold mb-1">
                      Стабільна робота інвертора
                    </p>

                    <small className="text-muted">
                      Помилок у роботі системи не виявлено
                    </small>

                  </div>

                  <small className="text-muted">
                    13:10
                  </small>

                </div>

              </div>

            </div>

          </div>

        </div>

      </div>

    </MainLayout>

  );
}

export default SolarPage;