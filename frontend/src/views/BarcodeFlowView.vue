<template>
  <section class="page">
    <div>
      <h1 class="page__title">Einlagerung</h1>
      <p class="page__subtitle">
        Produkt per Barcode erfassen und in ein Lagerfach einbuchen.
      </p>
    </div>
    <div class="soft-card">
  <h3 class="soft-card__title">Demo-Hinweis</h3>
  <p class="soft-card__text">
    Für die Vorführung kannst du bekannte Codes per Schnellwahl setzen oder einen unbekannten Barcode manuell testen.
  </p>
</div>

    <div class="card">
      <h2 class="card__title">1. Lagerfach auswählen</h2>

      <div class="form-stack" style="margin-top: 12px;">
        <div>
          <label class="field-label">Lager</label>
          <select v-model.number="selectedWarehouseId" class="text-input">
            <option :value="0">Bitte wählen</option>
            <option v-for="warehouse in warehouses" :key="warehouse.id" :value="warehouse.id">
              {{ warehouse.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="field-label">Regal</label>
          <select v-model.number="selectedShelfId" class="text-input" :disabled="!selectedWarehouse">
            <option :value="0">Bitte wählen</option>
            <option v-for="shelf in availableShelves" :key="shelf.id" :value="shelf.id">
              {{ shelf.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="field-label">Fach</label>
          <select v-model.number="selectedSlotId" class="text-input" :disabled="!selectedShelf">
            <option :value="0">Bitte wählen</option>
            <option v-for="slot in availableSlots" :key="slot.id" :value="slot.id">
              {{ slot.name }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="card__title">2. Barcode erfassen</h2>

      <div class="form-stack" style="margin-top: 12px;">
        <div>
          <label class="field-label">Barcode</label>
          <input
            v-model="barcode"
            class="text-input"
            type="text"
            placeholder="z. B. 4001234567890"
          />
        </div>

        <div class="quick-chips">
          <button type="button" class="chip-button" @click="barcode = '4001234567890'">Reis</button>
          <button type="button" class="chip-button" @click="barcode = '8076802085738'">Nudeln</button>
          <button type="button" class="chip-button" @click="barcode = '9999999999999'">Unbekannt</button>
        </div>

        <button type="button" class="primary-button" @click="lookupBarcode">
          Produkt prüfen
        </button>
      </div>
    </div>

    <div v-if="knownProduct" class="card">
      <h2 class="card__title">3. Bekanntes Produkt gefunden</h2>
      <p class="card__text">
        {{ knownProduct.name }} · {{ knownProduct.brand }} · {{ knownProduct.packSize }}
      </p>

      <div class="form-stack" style="margin-top: 12px;">
        <div>
          <label class="field-label">Menge</label>
          <input v-model.number="knownAmount" class="text-input" type="number" min="1" />
        </div>

        <div>
          <label class="field-label">MHD</label>
          <input v-model="knownMhd" class="text-input" type="date" />
        </div>

        <button type="button" class="primary-button" @click="storeKnownProduct">
          Bekanntes Produkt einlagern
        </button>
      </div>
    </div>

    <div v-if="showUnknownForm" class="card">
      <h2 class="card__title">3. Neues Produkt anlegen</h2>

      <div class="form-stack" style="margin-top: 12px;">
        <div>
          <label class="field-label">Name</label>
          <input v-model="newProduct.name" class="text-input" type="text" />
        </div>

        <div>
          <label class="field-label">Marke</label>
          <input v-model="newProduct.brand" class="text-input" type="text" />
        </div>

        <div>
          <label class="field-label">Packungsgröße</label>
          <input v-model="newProduct.packSize" class="text-input" type="text" placeholder="z. B. 500 g" />
        </div>

        <div>
          <label class="field-label">Erzeugnisgruppe</label>
          <select v-model="newProduct.category" class="text-input">
            <option>Getreideprodukte</option>
            <option>Getränke</option>
            <option>Fertiggerichte</option>
          </select>
        </div>

        <div>
          <label class="field-label">Menge</label>
          <input v-model.number="newProduct.menge" class="text-input" type="number" min="1" />
        </div>

        <div>
          <label class="field-label">Gewicht pro Einheit (kg)</label>
          <input v-model.number="newProduct.weightKg" class="text-input" type="number" min="0.1" step="0.1" />
        </div>

        <div>
          <label class="field-label">MHD</label>
          <input v-model="newProduct.mhd" class="text-input" type="date" />
        </div>

        <div>
          <label class="field-label">kcal pro 100 g</label>
          <input v-model.number="newProduct.kcal" class="text-input" type="number" min="0" />
        </div>

        <div class="inline-grid">
          <div>
            <label class="field-label">Protein</label>
            <input v-model.number="newProduct.protein" class="text-input" type="number" min="0" />
          </div>
          <div>
            <label class="field-label">Fett</label>
            <input v-model.number="newProduct.fat" class="text-input" type="number" min="0" />
          </div>
        </div>

        <div class="inline-grid">
          <div>
            <label class="field-label">Kohlenhydrate</label>
            <input v-model.number="newProduct.carbs" class="text-input" type="number" min="0" />
          </div>
          <div>
            <label class="field-label">Mindestbestand</label>
            <input v-model.number="newProduct.threshold" class="text-input" type="number" min="0" />
          </div>
        </div>

        <button type="button" class="primary-button" @click="createUnknownProduct">
          Neues Produkt anlegen und einlagern
        </button>
      </div>
    </div>

    <div v-if="successMessage" class="card success-card">
  <h2 class="card__title">Erfolgreich gespeichert</h2>
  <p class="card__text">{{ successMessage }}</p>
  <div class="top-space-sm">
    <RouterLink to="/lager" class="primary-button" style="display: inline-block;">
      Zum Lager
    </RouterLink>
  </div>
</div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '../services/api'
import type { Product, Shelf, Slot, Warehouse } from '../types'

const warehouses = ref<Warehouse[]>([])

const selectedWarehouseId = ref<number>(0)
const selectedShelfId = ref<number>(0)
const selectedSlotId = ref<number>(0)

const barcode = ref('')
const knownProduct = ref<Product | null>(null)
const showUnknownForm = ref(false)
const successMessage = ref('')

const knownAmount = ref(1)
const knownMhd = ref(new Date().toISOString().slice(0, 10))

const newProduct = ref({
  name: '',
  brand: '',
  packSize: '',
  category: 'Getreideprodukte',
  menge: 1,
  weightKg: 0.5,
  mhd: new Date().toISOString().slice(0, 10),
  barcode: '',
  kcal: 350,
  protein: 10,
  fat: 2,
  carbs: 70,
  threshold: 10,
})

onMounted(async () => {
  warehouses.value = await api.getWarehouses()
})

const selectedWarehouse = computed<Warehouse | null>(() => {
  return warehouses.value.find((item) => item.id === selectedWarehouseId.value) ?? null
})

const availableShelves = computed<Shelf[]>(() => {
  return selectedWarehouse.value?.shelves ?? []
})

const selectedShelf = computed<Shelf | null>(() => {
  return availableShelves.value.find((item) => item.id === selectedShelfId.value) ?? null
})

const availableSlots = computed<Slot[]>(() => {
  return selectedShelf.value?.slots ?? []
})

watch(selectedWarehouseId, () => {
  selectedShelfId.value = 0
  selectedSlotId.value = 0
})

watch(selectedShelfId, () => {
  selectedSlotId.value = 0
})

function resetResultState(): void {
  knownProduct.value = null
  showUnknownForm.value = false
  successMessage.value = ''
}

async function lookupBarcode(): Promise<void> {
  resetResultState()

  if (!selectedSlotId.value || !barcode.value.trim()) return

  const product = await api.findProductByBarcode(barcode.value.trim())

  if (product) {
    knownProduct.value = product
    knownMhd.value = product.mhd
  } else {
    showUnknownForm.value = true
    newProduct.value.barcode = barcode.value.trim()
    newProduct.value.name = ''
    newProduct.value.brand = ''
    newProduct.value.packSize = ''
  }
}

async function storeKnownProduct(): Promise<void> {
  if (!knownProduct.value || !selectedSlotId.value || knownAmount.value < 1) return

  const updated = await api.storeKnownProductInSlot({
    productId: knownProduct.value.id,
    slotId: selectedSlotId.value,
    menge: knownAmount.value,
    mhd: knownMhd.value,
  })

  if (!updated) return

  successMessage.value = `${updated.name} wurde mit ${knownAmount.value} Einheit(en) in das ausgewählte Fach eingebucht. Neuer Bestand: ${updated.menge}.`
  knownProduct.value = updated
  knownAmount.value = 1
}

async function createUnknownProduct(): Promise<void> {
  if (!selectedSlotId.value || !newProduct.value.name.trim()) return

  const created = await api.createProductAndStore({
    slotId: selectedSlotId.value,
    name: newProduct.value.name.trim(),
    brand: newProduct.value.brand.trim(),
    packSize: newProduct.value.packSize.trim(),
    category: newProduct.value.category,
    menge: newProduct.value.menge,
    weightKg: newProduct.value.weightKg,
    mhd: newProduct.value.mhd,
    barcode: newProduct.value.barcode,
    kcal: newProduct.value.kcal,
    protein: newProduct.value.protein,
    fat: newProduct.value.fat,
    carbs: newProduct.value.carbs,
    threshold: newProduct.value.threshold,
  })

  if (!created) return

  successMessage.value = `${created.name} wurde neu angelegt und in das ausgewählte Fach eingebucht.`
  showUnknownForm.value = false
}
</script>