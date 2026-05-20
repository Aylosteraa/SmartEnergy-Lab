import {
  PersonCircle,
  PlusLg,
  GeoAlt,
  BoxArrowRight
} from 'react-bootstrap-icons';

import {
  useState,
  useContext,
  useEffect
} from 'react';

import AddBuildingModal from '../components/AddBuildingModal';

import { useNavigate } from 'react-router-dom';

import { AuthContext } from '../context/AuthContext';

import {
  getUserCards,
  createUserCard,
} from '../api/userCardApi';


import type {
  UserCard,
  CreateUserCardData
} from "../api/userCardApi";

import {
  setActiveCard
} from "../utils/activeCard";


function ProfilePage() {

  const [showModal, setShowModal] = useState<boolean>(false);

  const [cards, setCards] = useState<UserCard[]>([]);

  const navigate = useNavigate();

  const { user, setUser } = useContext(AuthContext);


  // =====================================
  // LOAD USER CARDS
  // =====================================

  const loadCards = async () => {

    try {

      const data = await getUserCards();

      setCards(data);

    } catch (error) {

      console.error(error);
    }
  };


  useEffect(() => {

    loadCards();

  }, []);


  // =====================================
  // LOGOUT
  // =====================================

  const handleLogout = () => {

    localStorage.removeItem("token");

    setUser(null);

    navigate("/login");
  };


  // =====================================
  // CREATE CARD
  // =====================================

  const handleCreateCard = async (
    formData: CreateUserCardData
  ) => {

    try {

      await createUserCard(formData);

      setShowModal(false);

      loadCards();

    } catch (error) {

      console.error(error);

      alert("Адресу не знайдено");
    }
  };


  return (

    <div className="container py-5">

      {/* Header */} <div className="d-flex justify-content-between align-items-center mb-5"> 
        <div className="d-flex align-items-center gap-3"> 
          {/* <PersonCircle size={45} className="text-dark" /> <h1 className="fw-bold m-0"> Профіль </h1> */} 
          </div> 
          <button className="btn btn-outline-dark d-flex align-items-center gap-2" onClick={handleLogout} > 
            <BoxArrowRight size={20} /> 
              Вийти 
          </button> 
        </div>


      {/* User Info */}
      <div className="card shadow-sm border-0 p-4 mb-5 rounded-4">

        <div className="text-center">

          <PersonCircle
            size={100}
            className="text-secondary mb-3"
          />

          <h2 className="fw-bold">

            {user?.first_name} {user?.last_name}

          </h2>

          <p className="text-muted fs-5">

            {user?.email}

          </p>

        </div>

      </div>


      {/* Buildings */}
      <div className="d-flex justify-content-between align-items-center mb-4">

        <h3 className="fw-bold">
          Ваші об’єкти
        </h3>

      </div>


      <div className="row g-4">

        {/* USER CARDS */}
        {cards.map((card) => (

          <div
            className="col-md-4"
            key={card.id}
          >

            <div
              className="card shadow-sm border-0 rounded-4 p-4 h-100"
              style={{ cursor: 'pointer' }}

              onClick={() => {
                setActiveCard(card.id);
                navigate(`/`);
              }}
            >

              <div className="d-flex align-items-center gap-3 mb-3">

                <GeoAlt
                  size={28}
                  className="text-dark"
                />

                <h5 className="fw-bold m-0">
                  {card.title}
                </h5>

              </div>

              <p className="text-muted mb-2">
                {card.city}
              </p>

              <p className="text-muted mb-0">
                {card.street}
              </p>

            </div>

          </div>
        ))}


        {/* ADD CARD */}
        <div className="col-md-4">

          <button
            className="card border-2 border-dark border-dashed rounded-4 w-100 h-100 bg-white d-flex flex-column justify-content-center align-items-center p-4"
            style={{ minHeight: '220px' }}

            onClick={() => setShowModal(true)}
          >

            <PlusLg
              size={40}
              className="mb-3 text-dark"
            />

            <h5 className="fw-bold">
              Додати адресу
            </h5>

          </button>

        </div>

      </div>


      {/* MODAL */}
      <AddBuildingModal
        show={showModal}
        handleClose={() => setShowModal(false)}
        onCreate={handleCreateCard}
      />

    </div>
  );
}

export default ProfilePage;