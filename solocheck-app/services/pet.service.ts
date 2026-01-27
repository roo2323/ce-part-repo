import { api, getErrorMessage } from './api';
import type { Pet, CreatePetRequest, UpdatePetRequest, PetListResponse } from '@/types';

// API Response types (snake_case from backend)
interface PetApiResponse {
  id: string;
  user_id: string;
  name: string;
  species: string;
  breed: string | null;
  birth_date: string | null;
  weight: number | null;
  medical_notes: string | null;
  vet_info: string | null;
  caretaker_contact: string | null;
  photo_url: string | null;
  include_in_alert: boolean;
  created_at: string;
  updated_at: string;
}

interface PetListApiResponse {
  pets: PetApiResponse[];
  total: number;
}

// Transform API response to frontend format
const transformPet = (data: PetApiResponse): Pet => ({
  id: data.id,
  userId: data.user_id,
  name: data.name,
  species: data.species as Pet['species'],
  breed: data.breed || undefined,
  birthDate: data.birth_date || undefined,
  weight: data.weight || undefined,
  medicalNotes: data.medical_notes || undefined,
  vetInfo: data.vet_info || undefined,
  caretakerContact: data.caretaker_contact || undefined,
  photoUrl: data.photo_url || undefined,
  includeInAlert: data.include_in_alert,
  createdAt: data.created_at,
  updatedAt: data.updated_at,
});

export const petService = {
  /**
   * Get all pets for the current user
   */
  async getPets(): Promise<PetListResponse> {
    try {
      const response = await api.get<PetListApiResponse>('/pets');
      return {
        pets: response.data.pets.map(transformPet),
        total: response.data.total,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Get a specific pet by ID
   */
  async getPet(petId: string): Promise<Pet> {
    try {
      const response = await api.get<PetApiResponse>(`/pets/${petId}`);
      return transformPet(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Create a new pet
   */
  async createPet(data: CreatePetRequest): Promise<Pet> {
    try {
      const response = await api.post<PetApiResponse>('/pets', data);
      return transformPet(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Update a pet
   */
  async updatePet(petId: string, data: UpdatePetRequest): Promise<Pet> {
    try {
      const response = await api.put<PetApiResponse>(`/pets/${petId}`, data);
      return transformPet(response.data);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Delete a pet
   */
  async deletePet(petId: string): Promise<void> {
    try {
      await api.delete(`/pets/${petId}`);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};

export default petService;
