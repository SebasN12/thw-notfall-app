<template>
  <section class="page" v-if="product">
    <div>
      <button class="back-button" type="button" @click="router.back()">← Zurück</button>
    </div>

    <div class="card">
      <div class="product-header">
        <div>
          <h1 class="page__title" style="margin-bottom: 6px;">{{ product.name }}</h1>
          <p class="page__subtitle">{{ product.brand }} · {{ product.packSize }}</p>
        </div>
        <span class="status-pill" :class="stockStatusClass">
          {{ stockStatusText }}
        </span>
      </div>

      <div class="info-grid" style="margin-top: 16px;">
        <div class="info-box">
          <span class="info-box__label">Kategorie</span>
          <strong>{{ product.category }}</strong>
        </div>
        <div class="info-box">
          <span class="info-box__label">Menge</span>
          <strong>{{ product.menge }}</strong>
        </div>
        <div class="info-box">
          <span class="info-box__label">MHD</span>
          <strong>{{ product.mhd }}</strong>
        </div>
        <div class="info-box">
          <span class="info-box__label">Barcode</span>
          <strong>{{ product.barcode }}</strong>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="card__title">Nährwerte</h2>
      <div class="info-grid">
        <div class="info-box">
          <span class="info-box__label">kcal</span>
          <strong>{{ product.kcal }}</strong>
        </div>
        <div class="info-box">
          <span class="info-box__label">Protein</span>
          <strong>{{ product.protein }} g</strong>
        </div>
        <div class="info-box">
          <span class="info-box__label">Fett</span>
          <strong>{{ product.fat }} g</strong>
        </div>
        <div class="info-box">
          <span class="info-box__label">Kohlenhydrate</span>
          <strong>{{ product.carbs }} g</strong>
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
          <input v-model.number="amount" class="text-input" type="number" min="1" />
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

        <button type="button" class="primary-button" @click="submitBooking">
          {{ mode === 'remove' ? 'Entnahme buchen' : 'Einlagerung buchen' }}
        </button>
      </div>
    </div>

    <div class="card" v-if="lastAction">
      <h2 class="card__title">Letzte Aktion</h2>
      <p class="card__text">{{ lastAction }}</p>
    </div>
  </section>

  <section class="page" v-else>
    <div class="card">
      <h2 class="card__title">Produkt wird geladen ...</h2>
      <p class="card__text">Bitte kurz warten.</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../services/api'
import type { Product } from '../types'

const route = useRoute()
const router = useRouter()

const productId = Number(route.params.id)

const product = ref<Product | null>(null)
const amount = ref<number>(1)
const reason = ref<string>('')
const mode = ref<'remove' | 'add'>('remove')
const lastAction = ref<string>('')

onMounted(async () => {
  product.value = await api.getProductById(productId)
})

const stockStatusClass = computed(() => {
  if (!product.value) return 'status-pill--neutral'
  if (product.value.menge < product.value.threshold) return 'status-pill--danger'
  if (product.value.menge < product.value.threshold * 1.5) return 'status-pill--warning'
  return 'status-pill--success'
})

const stockStatusText = computed(() => {
  if (!product.value) return 'Lädt'
  if (product.value.menge < product.value.threshold) return 'Kritisch'
  if (product.value.menge < product.value.threshold * 1.5) return 'Knapp'
  return 'OK'
})

async function submitBooking(): Promise<void> {
  if (!product.value || !amount.value || amount.value < 1) return

  if (mode.value === 'remove') {
    const updated = await api.removeStock({
      productId: product.value.id,
      amount: amount.value,
      reason: reason.value,
    })

    if (updated) {
      product.value = updated
      lastAction.value = `${amount.value} Einheit(en) von ${updated.name} entnommen${reason.value ? ` – Grund: ${reason.value}` : ''}. Neuer Bestand: ${updated.menge}.`
    }
  } else {
    const updated = await api.addStock({
      productId: product.value.id,
      amount: amount.value,
      reason: reason.value,
    })

    if (updated) {
      product.value = updated
      lastAction.value = `${amount.value} Einheit(en) von ${updated.name} eingelagert${reason.value ? ` – Hinweis: ${reason.value}` : ''}. Neuer Bestand: ${updated.menge}.`
    }
  }

  amount.value = 1
  reason.value = ''
}
</script>