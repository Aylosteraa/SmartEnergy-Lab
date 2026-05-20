export const setActiveCard = (
  cardId: number
) => {

  localStorage.setItem(
    "active_card_id",
    cardId.toString()
  );
};


export const getActiveCard = (): number | null => {

  const cardId =
    localStorage.getItem("active_card_id");

  return cardId ? Number(cardId) : null;
};


export const clearActiveCard = () => {

  localStorage.removeItem(
    "active_card_id"
  );
};