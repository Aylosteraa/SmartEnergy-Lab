import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {AuthContext} from '../context/AuthContext';

import { loginUser } from '../api/authApi';
import { getCurrentUser } from '../api/authApi';

function LoginPage() {

  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [error, setError] = useState('');

  const { setUser } = useContext(AuthContext);

  const handleLogin = async (
  e: React.FormEvent
) => {

  e.preventDefault();

  try {

    const response = await loginUser(
      email,
      password
    );

    localStorage.setItem(
      "token",
      response.access_token
    );

    const userData =
      await getCurrentUser();

    setUser(userData);

    navigate("/profile");

  } catch (error) {

    setError(
      "Невірний email або пароль"
    );
  }
};

  return (

    <div className="container-fluid vh-100 d-flex justify-content-center align-items-center bg-light">

      <div
        className="card shadow p-4"
        style={{ width: '400px' }}
      >

        <h2 className="text-center mb-4">
          Вхід
        </h2>

        <form onSubmit={handleLogin}>

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
                setEmail(e.target.value)
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
                setPassword(e.target.value)
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
            Увійти
          </button>

        </form>

        <p className="text-center mt-3">

          Ще не маєте аккаунту?

          <Link
            to="/register"
            className="ms-1 text-dark text-decoration-underline"
          >
            Зареєструйтеся
          </Link>

        </p>

      </div>

    </div>
  );
}

export default LoginPage;