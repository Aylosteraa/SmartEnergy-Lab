import API from "./api";

export const loginUser = async (
  email: string,
  password: string
) => {

  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  const response = await API.post(
    "/auth/login",
    formData,
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
};

export const registerUser = async (data: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}) => {

  const response = await API.post(
    "/auth/register",
    data
  );

  return response.data;
};


export const getCurrentUser = async () => {

  const response = await API.get(
    "/users/data"
  );

  return response.data;
};