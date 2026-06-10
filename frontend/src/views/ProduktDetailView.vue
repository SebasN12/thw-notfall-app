<template>
  <section class="page" v-if="loading">
    <div class="loading-state">
      <div class="loading-dots">
        <span></span><span></span><span></span>
      </div>
      <div>Produkt wird geladen ...</div>
    </div>
  </section>

  <section class="page" v-else-if="errorMessage">
    <div class="card">
      <h2 class="card__title">Fehler</h2>
      <p class="card__text">{{ errorMessage }}</p>

      <div class="top-space-sm">
        <button class="back-button" type="button" @click="router.back()">
          ← Zurück
        </button>
      </div>
    </div>
  </section>

  <section class="page" v-else-if="product">
    <div>
      <button class="back-button" type="button" @click="router.back()">← Zurück</button>
    </div>

    <div class="card">
      <div class="product-header">
        <div>
          <h1 class="page__title" style="margin-bottom: 6px;">
            {{ product.name ?? 'Unbenanntes Produkt' }}
          </h1>
          <p class="page__subtitle">
            {{ product.marke ?? 'Keine Marke' }} · {{ product.menge ?? 'Keine Packungsgröße' }}
          </p>
        </div>

        <span class="status-pill" :class="stockStatusClass">
          {{ stockStatusText }}
        </span>
      </div>

      <div class="info-grid" style="margin-top: 16px;">
        <div class="info-box">
          <span class="info-box__label">Erzeugnisgruppe</span>
          <strong>{{ product.erzeugnisgruppe ?? '–' }}</strong>
        </div>

        <div class="info-box">
          <span class="info-box__label">Bestand</span>
          <strong>{{ product.menge_eingelagert }}</strong>
        </div>

        <div class="info-box">
          <span class="info-box__label">Geöffnet</span>
          <strong>{{ product.menge_geoeffnet }}</strong>
        </div>

        <div class="info-box">
          <span class="info-box__label">MHD</span>
          <strong>{{ product.mhd ?? 'Kein MHD' }}</strong>
        </div>

        <div class="info-box">
          <span class="info-box__label">Barcode</span>
          <strong>{{ product.barcode ?? '–' }}</strong>
        </div>

        <div class="info-box">
          <span class="info-box__label">Lagerort</span>
          <strong>
            {{ product.warehouse_name ?? '–' }} /
            {{ product.regal_bezeichnung ?? '–' }} /
            Fach {{ product.lagerfach_position ?? product.lagerfach_id }}
          </strong>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="card__title">Nährwerte</h2>

      <div class="info-grid">
        <div class="info-box">
          <span class="info-box__label">kcal</span>
          <strong>{{ product.naehrwerte.kcal ?? 0 }}</strong>
        </div>

        <div class="info-box">
          <span class="info-box__label">Protein</span>
          <strong>{{ product.naehrwerte.protein ?? 0 }} g</strong>
        </div>

        <div class="info-box">
          <span class="info-box__label">Fett</span>
          <strong>{{ product.naehrwerte.fett ?? 0 }} g</strong>
        </div>

        <div class="info-box">
          <span class="info-box__label">Kohlenhydrate</span>
          <strong>{{ product.naehrwerte.kohlenhydrate ?? 0 }} g</strong>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="card__title">Bestand buchen</h2>

      <div class="segmented">
        <button
          type="button"
          class="segmented__item"
          :class="{ 'segmented__item--active': mode === 'remove' }"
          @click="mode = 'remove'"
        >
          Entnahme
        </button>

        <button
          type="button"
          class="segmented__item"
          :class="{ 'segmented__item--active': mode === 'add' }"
          @click="mode = 'add'"
        >
          Einlagerung
        </button>
      </div>

      <div class="form-stack">
        <div>
          <label class="field-label">Menge</label>
          <input
            v-model.number="amount"
            class="text-input"
            type="number"
            min="1"
            :max="mode === 'remove' ? product.menge_eingelagert : undefined"
          />
        </div>

        <div v-if="mode === 'add'">
          <label class="field-label">MHD</label>
          <input v-model="bestBefore" class="text-input" type="date" />
        </div>

        <div>
          <label class="field-label">
            {{ mode === 'remove' ? 'Grund (optional)' : 'Hinweis (optional)' }}
          </label>
          <input
            v-model="reason"
            class="text-input"
            type="text"
            :placeholder="mode === 'remove' ? 'z. B. Einsatz, Ablauf' : 'z. B. Lieferung, Nachschub'"
          />
        </div>

        <button
          type="button"
          class="primary-button"
          :disabled="bookingLoading"
          @click="submitBooking"
        >
          {{
            bookingLoading
              ? 'Wird gebucht ...'
              : mode === 'remove'
                ? 'Entnahme buchen'
                : 'Einlagerung buchen'
          }}
        </button>
      </div>
    </div>

    <div class="card success-card" v-if="lastAction">
      <h2 class="card__title">Letzte Aktion</h2>
      <p class="card__text">{{ lastAction }}</p>
    </div>
  </section>

  <section class="page" v-else>
    <div class="card">
      <h2 class="card__title">Produkt nicht gefunden</h2>
      <p class="card__text">Bitte öffne das Produkt erneut über die Lageransicht.</p>
      <div class="top-space-sm">
        <RouterLink to="/lager" class="primary-button" style="display: inline-block;">
          Zur Lageransicht
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { StockDetail } from '../types'
import { addStock, getStockDetail, removeStock } from '../services/stockApi'

const route = useRoute()
const router = useRouter()

const stockId = Number(route.params.id)

const product = ref<StockDetail | null>(null)
const amount = ref<number>(1)
const reason = ref<string>('')
const bestBefore = ref<string>(new Date().toISOString().slice(0, 10))
const mode = ref<'remove' | 'add'>('remove')

const loading = ref(true)
const bookingLoading = ref(false)
const errorMessage = ref('')
const lastAction = ref('')

// Demo-User, weil User-Management laut Scope nicht umgesetzt wird.
const DEMO_USER_ID = 1

onMounted(async () => {
  await loadProduct(stockId)
})

async function loadProduct(id: number): Promise<void> {
  loading.value = true
  errorMessage.value = ''

  try {
    product.value = await getStockDetail(id)
  } catch (error) {
    console.error(error)
    errorMessage.value = 'Produktdetails konnten nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

const stockStatusClass = computed(() => {
  if (!product.value) return 'status-pill--neutral'

  if (product.value.menge_eingelagert <= 0) return 'status-pill--danger'
  if (product.value.menge_eingelagert < 5) return 'status-pill--warning'

  return 'status-pill--success'
})

const stockStatusText = computed(() => {
  if (!product.value) return 'Lädt'

  if (product.value.menge_eingelagert <= 0) return 'Leer'
  if (product.value.menge_eingelagert < 5) return 'Knapp'

  return 'OK'
})

async function submitBooking(): Promise<void> {
  if (!product.value || !amount.value || amount.value < 1) return

  errorMessage.value = ''
  lastAction.value = ''

  if (mode.value === 'remove' && amount.value > product.value.menge_eingelagert) {
    errorMessage.value = 'Die Entnahmemenge darf nicht größer als der aktuelle Bestand sein.'
    return
  }

  bookingLoading.value = true

  try {
    if (mode.value === 'remove') {
      const response = await removeStock({
        stock_id: product.value.stock_id,
        user_id: DEMO_USER_ID,
        quantity: amount.value,
        reason: reason.value || null,
      })

      lastAction.value = `${amount.value} Einheit(en) von ${product.value.name ?? 'Produkt'} entnommen${
        reason.value ? ` – Grund: ${reason.value}` : ''
      }. Neuer Bestand: ${response.quantity}.`

      if (response.quantity <= 0) {
        product.value = {
          ...product.value,
          menge_eingelagert: 0,
        }
      } else {
        await loadProduct(response.stock_id)
      }
    } else {
      const response = await addStock({
        shelf_slot_id: product.value.shelf_slot_id,
        product_id: product.value.produkt_id,
        user_id: DEMO_USER_ID,
        quantity: amount.value,
        best_before: bestBefore.value || null,
        stored_at: new Date().toISOString().slice(0, 10),
        reason: reason.value || null,
      })

      lastAction.value = `${amount.value} Einheit(en) von ${product.value.name ?? 'Produkt'} eingelagert${
        reason.value ? ` – Hinweis: ${reason.value}` : ''
      }. Neuer Bestand: ${response.quantity}.`

      await loadProduct(response.stock_id)
    }

    amount.value = 1
    reason.value = ''
  } catch (error) {
    console.error(error)
    errorMessage.value = 'Die Buchung konnte nicht durchgeführt werden.'
  } finally {
    bookingLoading.value = false
  }
}
</script>