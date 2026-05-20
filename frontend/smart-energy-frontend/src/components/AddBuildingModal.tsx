import {
  Modal,
  Button
} from 'react-bootstrap';

import { useState } from 'react';

import type {
  CreateUserCardData
} from '../api/userCardApi';


type Props = {

  show: boolean;

  handleClose: () => void;

  onCreate: (
    formData: CreateUserCardData
  ) => Promise<void>;
};


function AddBuildingModal({

  show,
  handleClose,
  onCreate

}: Props) {

  const [title, setTitle] = useState("");

  const [city, setCity] = useState("");

  const [street, setStreet] = useState("");


  // =====================================
  // SUBMIT
  // =====================================

  const handleSubmit = async (
    e: React.FormEvent
  ) => {

    e.preventDefault();

    await onCreate({
      title,
      city,
      street
    });

    setTitle("");
    setCity("");
    setStreet("");
  };


  return (

    <Modal
      show={show}
      onHide={handleClose}
      centered
    >

      <form onSubmit={handleSubmit}>

        <Modal.Header closeButton>

          <Modal.Title>
            Додати новий об’єкт
          </Modal.Title>

        </Modal.Header>


        <Modal.Body>

          {/* TITLE */}
          <div className="mb-3">

            <label className="form-label">
              Назва об’єкта
            </label>

            <input
              type="text"
              className="form-control"

              placeholder="Наприклад: Дача"

              value={title}

              onChange={(e) =>
                setTitle(e.target.value)
              }

              required
            />

          </div>


          {/* CITY */}
          <div className="mb-3">

            <label className="form-label">
              Місто
            </label>

            <input
              type="text"
              className="form-control"

              placeholder="Введіть місто"

              value={city}

              onChange={(e) =>
                setCity(e.target.value)
              }

              required
            />

          </div>


          {/* STREET */}
          <div className="mb-3">

            <label className="form-label">
              Адреса
            </label>

            <input
              type="text"
              className="form-control"

              placeholder="Введіть адресу"

              value={street}

              onChange={(e) =>
                setStreet(e.target.value)
              }

              required
            />

          </div>

        </Modal.Body>


        <Modal.Footer>

          <Button
            variant="secondary"
            onClick={handleClose}
          >

            Скасувати

          </Button>

          <Button
            variant="dark"
            type="submit"
          >

            Зберегти

          </Button>

        </Modal.Footer>

      </form>

    </Modal>

  );
}

export default AddBuildingModal;