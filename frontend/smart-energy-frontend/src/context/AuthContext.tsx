import {
  createContext,
  useEffect,
  useState
} from "react";

import { getCurrentUser } from "../api/authApi";

export const AuthContext = createContext<any>(null);

export function AuthProvider({
  children
}: any) {

  const [user, setUser] = useState(null);

  useEffect(() => {

    const loadUser = async () => {

      try {

        const data = await getCurrentUser();

        setUser(data);

      } catch {

        setUser(null);
      }
    };

    loadUser();

  }, []);

  return (
    <AuthContext.Provider
      value={{ user, setUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}