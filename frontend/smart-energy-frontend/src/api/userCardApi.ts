import API from "./api";


export interface UserCard {
    id: number;
    title: string;
    city: string;
    street: string;
}


export interface CreateUserCardData {
    title: string;
    city: string;
    street: string;
}


// =====================================
// GET USER CARDS
// =====================================

export const getUserCards = async (): Promise<UserCard[]> => {

    const response = await API.get<UserCard[]>(
        "/cards"
    );

    return response.data;
};


// =====================================
// CREATE USER CARD
// =====================================

export const createUserCard = async (
    data: CreateUserCardData
): Promise<UserCard> => {

    const response = await API.post<UserCard>(
        "/cards",
        data
    );

    return response.data;
};