import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

const USER_KEY = "jobboard_user_token";
const ADMIN_KEY = "jobboard_admin_token";

type AuthContextValue = {
  userToken: string | null;
  adminToken: string | null;
  setUserToken: (t: string | null) => void;
  setAdminToken: (t: string | null) => void;
  logoutUser: () => void;
  logoutAdmin: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userToken, setUserTokenState] = useState<string | null>(() =>
    typeof localStorage !== "undefined" ? localStorage.getItem(USER_KEY) : null
  );
  const [adminToken, setAdminTokenState] = useState<string | null>(() =>
    typeof localStorage !== "undefined" ? localStorage.getItem(ADMIN_KEY) : null
  );

  useEffect(() => {
    if (userToken) localStorage.setItem(USER_KEY, userToken);
    else localStorage.removeItem(USER_KEY);
  }, [userToken]);

  useEffect(() => {
    if (adminToken) localStorage.setItem(ADMIN_KEY, adminToken);
    else localStorage.removeItem(ADMIN_KEY);
  }, [adminToken]);

  const setUserToken = useCallback((t: string | null) => {
    setUserTokenState(t);
  }, []);

  const setAdminToken = useCallback((t: string | null) => {
    setAdminTokenState(t);
  }, []);

  const logoutUser = useCallback(() => setUserTokenState(null), []);
  const logoutAdmin = useCallback(() => setAdminTokenState(null), []);

  const value = useMemo(
    () =>
      ({
        userToken,
        adminToken,
        setUserToken,
        setAdminToken,
        logoutUser,
        logoutAdmin,
      }) satisfies AuthContextValue,
    [adminToken, userToken, setUserToken, setAdminToken, logoutUser, logoutAdmin]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
