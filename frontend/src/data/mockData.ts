import type { Warehouse } from '../types'

export const warehouses: Warehouse[] = [
  {
    id: 1,
    name: 'Hauptlager',
    shelves: [
      {
        id: 1,
        name: 'Regal A',
        slots: [
          {
            id: 1,
            name: 'Fach A1',
            products: [
              {
                id: 1,
                name: 'Reis',
                brand: 'Ja!',
                packSize: '1 kg',
                category: 'Getreideprodukte',
                menge: 50,
                mhd: '2026-06-01',
                barcode: '4001234567890',
                kcal: 360,
                protein: 7,
                fat: 1,
                carbs: 79,
                threshold: 20,
                weightKg: 1,
              },
              {
                id: 2,
                name: 'Nudeln',
                brand: 'Barilla',
                packSize: '500 g',
                category: 'Getreideprodukte',
                menge: 30,
                mhd: '2026-05-20',
                barcode: '8076802085738',
                kcal: 350,
                protein: 12,
                fat: 2,
                carbs: 70,
                threshold: 15,
                weightKg: 0.5,
              },
            ],
          },
          {
            id: 2,
            name: 'Fach A2',
            products: [
              {
                id: 3,
                name: 'Mineralwasser',
                brand: 'Gerolsteiner',
                packSize: '0,5 L',
                category: 'Getränke',
                menge: 100,
                mhd: '2027-01-01',
                barcode: '4066600101234',
                kcal: 0,
                protein: 0,
                fat: 0,
                carbs: 0,
                threshold: 40,
                weightKg: 0.5,
              },
            ],
          },
        ],
      },
      {
        id: 2,
        name: 'Regal B',
        slots: [
          {
            id: 3,
            name: 'Fach B1',
            products: [
              {
                id: 4,
                name: 'Konservensuppe',
                brand: 'Erasco',
                packSize: '800 ml',
                category: 'Fertiggerichte',
                menge: 18,
                mhd: '2026-05-01',
                barcode: '4305615123001',
                kcal: 55,
                protein: 2,
                fat: 2,
                carbs: 7,
                threshold: 25,
                weightKg: 0.8,
              },
            ],
          },
        ],
      },
    ],
  },
  {
    id: 2,
    name: 'Außenlager',
    shelves: [
      {
        id: 3,
        name: 'Regal C',
        slots: [
          {
            id: 4,
            name: 'Fach C1',
            products: [
              {
                id: 5,
                name: 'Haferflocken',
                brand: 'Kölln',
                packSize: '500 g',
                category: 'Getreideprodukte',
                menge: 22,
                mhd: '2026-06-20',
                barcode: '4000540001234',
                kcal: 370,
                protein: 13,
                fat: 7,
                carbs: 58,
                threshold: 12,
                weightKg: 0.5,
              },
            ],
          },
        ],
      },
    ],
  },
]