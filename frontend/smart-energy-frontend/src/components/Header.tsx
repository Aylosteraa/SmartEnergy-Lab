import {
  useContext,
  useEffect,
  useState
} from 'react';

import {
  GeoAlt,
  PersonCircle,
  BellFill
} from 'react-bootstrap-icons';

import {
  Dropdown
} from 'react-bootstrap';

import {
  useNavigate
} from 'react-router-dom';

import {
  AuthContext
} from '../context/AuthContext';

import {
  setActiveCard,
  getActiveCard
} from "../utils/activeCard";

import {
  getUserCards
} from '../api/userCardApi';

import type {
  UserCard
} from '../api/userCardApi';


function Header() {

  const navigate = useNavigate();

  const { user } = useContext(AuthContext);

  const [cards, setCards] =
    useState<UserCard[]>([]);

  const [activeCard, setActiveCardState] =
    useState<UserCard | null>(null);

  const [notifications, setNotifications] =
    useState<any[]>([]);


  // =====================================
  // LOAD USER CARDS
  // =====================================

  useEffect(() => {

    const loadCards = async () => {

      try {

        const data = await getUserCards();

        setCards(data);

        // ================================
        // ACTIVE CARD
        // ================================

        const activeCardId =
          getActiveCard();

        if (activeCardId) {

          const foundCard = data.find(
            (card) => card.id === activeCardId
          );

          if (foundCard) {

            setActiveCardState(foundCard);
          }
        }

        // ================================
        // DEFAULT FIRST CARD
        // ================================

        else if (data.length > 0) {

          setActiveCard(data[0].id);

          setActiveCardState(data[0]);
        }

      } catch (error) {

        console.error(error);
      }
    };

    loadCards();

  }, []);


  // =====================================
  // LOAD NOTIFICATIONS
  // =====================================

  useEffect(() => {

    const loadNotifications = async () => {

      try {

        if (!user?.id) return;

        const response = await fetch(

          `http://127.0.0.1:8000/notifications/latest/${user.id}`
        );

        const data = await response.json();

        setNotifications(data);

      } catch (error) {

        console.error(error);
      }
    };

    loadNotifications();

    // refresh every 30 sec

    const interval = setInterval(
      loadNotifications,
      30000
    );

    return () => clearInterval(interval);

  }, [user]);


  // =====================================
  // CHANGE ACTIVE CARD
  // =====================================

  const handleSelectCard = (
    card: UserCard
  ) => {

    setActiveCard(card.id);

    setActiveCardState(card);

    navigate("/");
  };


  return (

    <div
      className="
        d-flex
        justify-content-between
        align-items-center
        bg-white
        shadow-sm
        px-4
        py-3
        rounded-4
        mb-4
      "
    >

      {/* ================================= */}
      {/* ACTIVE CARD */}
      {/* ================================= */}

      <Dropdown>

        <Dropdown.Toggle
          variant="light"
          className="
            border-0
            p-0
            bg-white
            shadow-none
            d-flex
            align-items-center
            gap-2
          "
        >

          <GeoAlt
            size={20}
            className="text-dark"
          />

          <h5 className="fw-bold m-0 text-dark">

            {activeCard?.title || "Оберіть об’єкт"}

          </h5>

        </Dropdown.Toggle>


        <Dropdown.Menu
          className="
            shadow
            border-0
            rounded-4
          "
        >

          {cards.map((card) => (

            <Dropdown.Item
              key={card.id}

              onClick={() =>
                handleSelectCard(card)
              }
            >

              {card.title}

            </Dropdown.Item>

          ))}

        </Dropdown.Menu>

      </Dropdown>


      {/* ================================= */}
      {/* RIGHT SIDE */}
      {/* ================================= */}

      <div
        className="
          d-flex
          align-items-center
          gap-4
        "
      >

        {/* ============================== */}
        {/* NOTIFICATIONS */}
        {/* ============================== */}

        <Dropdown align="end">

          <Dropdown.Toggle
            variant="light"
            className="
              border-0
              bg-white
              shadow-none
              position-relative
            "
          >

            <BellFill
              size={24}
              className="text-dark"
            />

            {notifications.length > 0 && (

              <span
                className="
                  position-absolute
                  top-0
                  start-100
                  translate-middle
                  badge
                  rounded-pill
                  bg-danger
                "
              >

                {notifications.length}

              </span>
            )}

          </Dropdown.Toggle>

          <Dropdown.Menu
            className="
              shadow
              border-0
              rounded-4
              p-0
              overflow-hidden
            "
            style={{
              width: "420px",
              maxHeight: "500px",
              overflowY: "auto"
            }}
          >

            {/* HEADER */}

            <div
              className="
                p-3
                border-bottom
                bg-light
              "
            >

              <h6 className="fw-bold mb-0">

                Сповіщення системи

              </h6>

            </div>


            {/* EMPTY */}

            {notifications.length === 0 && (

              <div
                className="
                  p-4
                  text-center
                  text-muted
                "
              >

                Немає нових сповіщень

              </div>
            )}


            {/* NOTIFICATIONS */}

            {notifications.map((notification) => (

              <Dropdown.Item
                key={notification.id}
                className="
                  border-bottom
                  p-3
                "
              >

                <div>

                  {/* TITLE */}

                  <div
                    className="
                      d-flex
                      justify-content-between
                      align-items-start
                      mb-1
                    "
                  >

                    <h6 className="fw-bold mb-0">

                      {notification.title}

                    </h6>

                    <small className="text-muted">

                      {
                        new Date(
                          notification.created_at
                        ).toLocaleTimeString(
                          "uk-UA",
                          {
                            hour: "2-digit",
                            minute: "2-digit"
                          }
                        )
                      }

                    </small>

                  </div>


                  {/* MESSAGE */}

                  <p
                    className="
                      small
                      text-muted
                      mb-0
                    "
                  >

                    {notification.message}

                  </p>

                </div>

              </Dropdown.Item>
            ))}

          </Dropdown.Menu>

        </Dropdown>


        {/* ============================== */}
        {/* USER */}
        {/* ============================== */}

        <div
          className="
            d-flex
            align-items-center
            gap-3
          "
          style={{ cursor: 'pointer' }}

          onClick={() =>
            navigate('/profile')
          }
        >

          <div className="text-end">

            <p className="fw-bold mb-0">

              {user?.first_name}
              {" "}
              {user?.last_name}

            </p>

            <small className="text-muted">

              {user?.email}

            </small>

          </div>

          <PersonCircle
            size={45}
            className="text-dark"
          />

        </div>

      </div>

    </div>
  );
}

export default Header;