export const initialStore = () => {
  return {
    message: null,
    todos: [
      {
        id: 1,
        title: "Make the bed",
        background: null,
      },
      {
        id: 2,
        title: "Do my homework",
        background: null,
      }
    ],
    user: null,           // puedes almacenar info de sesión si decides
    patientData: null,    // para registrar paciente
  };
};

export default function storeReducer(store, action = {}) {
  switch (action.type) {
    case 'set_hello':
      return {
        ...store,
        message: action.payload
      };

    case 'add_task':
      const { id, color } = action.payload;
      return {
        ...store,
        todos: store.todos.map((todo) => (todo.id === id ? { ...todo, background: color } : todo))
      };

    // Nueva acción para guardar datos de paciente
    case 'REGISTER_PATIENT':
      return {
        ...store,
        patientData: action.payload
      };

    // Placeholder para login
    case 'LOGIN_USER':
      return {
        ...store,
        user: action.payload
      };

    // Placeholder para logout
    case 'LOGOUT_USER':
      return {
        ...store,
        user: null
      };

    default:
      console.warn(`⚠️ Acción desconocida: ${action.type}`);
      return store;
  }
}
