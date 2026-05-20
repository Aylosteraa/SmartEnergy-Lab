import { useState, useContext } from 'react';
import {Link, useNavigate} from 'react-router-dom';

import { registerUser, getCurrentUser } from '../api/authApi';

import { AuthContext } from '../context/AuthContext';

function RegisterPage() {

  const navigate = useNavigate();

  const { setUser } = useContext(AuthContext);

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [confirmPassword, setConfirmPassword] = useState('');

  const [error, setError] = useState('');

  const handleRegister = async (
    e: React.FormEvent
  ) => {

    e.preventDefault();

    if (password !== confirmPassword) {

      setError(
        'Паролі не співпадають'
      );

      return;
    }

    try {

      const response =
        await registerUser({

          email,

          first_name: firstName,

          last_name: lastName,

          password,
        });

      localStorage.setItem(
        'token',
        response.access_token
      );

      const userData =
        await getCurrentUser();

      setUser(userData);

      navigate('/profile');

    } catch (error) {

      setError(
        'Помилка реєстрації'
      );

      console.error(error);
    }
  };

  return (

    <div className="container-fluid vh-100 d-flex justify-content-center align-items-center bg-light">

      <div
        className="card shadow p-4"
        style={{ width: '450px' }}
      >

        <h2 className="text-center mb-4">
          Реєстрація
        </h2>

        <form onSubmit={handleRegister}>

          <div className="mb-3">

            <label className="form-label">
              Ім’я
            </label>

            <input
              type="text"
              className="form-control"
              placeholder="Введіть ім’я"
              value={firstName}
              onChange={(e) =>
                setFirstName(
                  e.target.value
                )
              }
            />

          </div>

          <div className="mb-3">

            <label className="form-label">
              Прізвище
            </label>

            <input
              type="text"
              className="form-control"
              placeholder="Введіть прізвище"
              value={lastName}
              onChange={(e) =>
                setLastName(
                  e.target.value
                )
              }
            />

          </div>

          <div className="mb-3">

            <label className="form-label">
              Email
            </label>

            <input
              type="email"
              className="form-control"
              placeholder="Введіть email"
              value={email}
              onChange={(e) =>
                setEmail(
                  e.target.value
                )
              }
            />

          </div>

          <div className="mb-3">

            <label className="form-label">
              Пароль
            </label>

            <input
              type="password"
              className="form-control"
              placeholder="Введіть пароль"
              value={password}
              onChange={(e) =>
                setPassword(
                  e.target.value
                )
              }
            />

          </div>

          <div className="mb-4">

            <label className="form-label">
              Підтвердження пароля
            </label>

            <input
              type="password"
              className="form-control"
              placeholder="Повторіть пароль"
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(
                  e.target.value
                )
              }
            />

          </div>

          {error && (

            <div className="alert alert-danger">

              {error}

            </div>
          )}

          <button
            type="submit"
            className="btn btn-dark w-100"
          >
            Зареєструватися
          </button>

        </form>

        <p className="text-center mt-3">

          Уже є аккаунт?

          <Link
            to="/login"
            className="ms-1 text-dark text-decoration-underline"
          >
            Увійдіть в систему
          </Link>

        </p>

      </div>

    </div>
  );
}

export default RegisterPage;