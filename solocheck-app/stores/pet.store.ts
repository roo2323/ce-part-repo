import { create } from 'zustand';
import { petService } from '@/services/pet.service';
import type { Pet, CreatePetRequest, UpdatePetRequest } from '@/types';

interface PetState {
  pets: Pet[];
  isLoading: boolean;
  error: string | null;
}

interface PetActions {
  fetchPets: () => Promise<void>;
  createPet: (data: CreatePetRequest) => Promise<Pet>;
  updatePet: (petId: string, data: UpdatePetRequest) => Promise<Pet>;
  deletePet: (petId: string) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

type PetStore = PetState & PetActions;

const initialState: PetState = {
  pets: [],
  isLoading: false,
  error: null,
};

export const usePetStore = create<PetStore>((set, get) => ({
  ...initialState,

  fetchPets: async () => {
    set({ isLoading: true, error: null });
    try {
      const result = await petService.getPets();
      set({ pets: result.pets, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '반려동물 목록을 불러오는데 실패했습니다.',
      });
      throw error;
    }
  },

  createPet: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const pet = await petService.createPet(data);
      set((state) => ({
        pets: [...state.pets, pet],
        isLoading: false,
      }));
      return pet;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '반려동물 등록에 실패했습니다.',
      });
      throw error;
    }
  },

  updatePet: async (petId, data) => {
    set({ isLoading: true, error: null });
    try {
      const updatedPet = await petService.updatePet(petId, data);
      set((state) => ({
        pets: state.pets.map((pet) => (pet.id === petId ? updatedPet : pet)),
        isLoading: false,
      }));
      return updatedPet;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '반려동물 정보 수정에 실패했습니다.',
      });
      throw error;
    }
  },

  deletePet: async (petId) => {
    set({ isLoading: true, error: null });
    try {
      await petService.deletePet(petId);
      set((state) => ({
        pets: state.pets.filter((pet) => pet.id !== petId),
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '반려동물 삭제에 실패했습니다.',
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set(initialState);
  },
}));

export default usePetStore;
