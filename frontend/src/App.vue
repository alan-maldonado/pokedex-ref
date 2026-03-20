<template>
  <div class="min-h-screen bg-gray-100">

    <!-- Header -->
    <header class="bg-red-600 shadow-lg">
      <div class="max-w-4xl mx-auto px-4 pt-4 pb-0">

        <!-- Game title + selector -->
        <div class="flex items-center gap-3 mb-3">
          <div class="w-8 h-8 rounded-full bg-white border-4 border-gray-800 flex-shrink-0" />
          <div class="relative" ref="gameDropdownRef">
            <p class="text-white/60 text-xs uppercase tracking-widest leading-none mb-0.5">Pokédex</p>

            <!-- Single game: plain title -->
            <h1 v-if="games.length <= 1" class="text-xl font-bold text-white tracking-wide">
              {{ selectedGame?.name ?? '…' }}
            </h1>

            <!-- Multiple games: dropdown button -->
            <div v-else>
              <button
                @click="gameDropdownOpen = !gameDropdownOpen"
                class="flex items-center gap-2 text-xl font-bold text-white tracking-wide hover:text-white/80 transition-colors"
              >
                {{ selectedGame?.name ?? '…' }}
                <svg
                  :class="['w-4 h-4 transition-transform', gameDropdownOpen ? 'rotate-180' : '']"
                  fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6"/>
                </svg>
              </button>

              <div
                v-if="gameDropdownOpen"
                class="absolute top-full left-0 mt-2 bg-white rounded-xl shadow-xl z-50 overflow-hidden min-w-56"
              >
                <button
                  v-for="g in games"
                  :key="g.slug"
                  @click="selectedGameSlug = g.slug; gameDropdownOpen = false"
                  :class="[
                    'w-full text-left px-4 py-3 text-sm font-medium transition-colors',
                    g.slug === selectedGameSlug
                      ? 'bg-red-50 text-red-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  ]"
                >
                  {{ g.name }}
                  <span class="block text-xs text-gray-400 font-normal">{{ g.year }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Dex tabs -->
        <div class="flex gap-1" v-if="selectedGame">
          <button
            v-for="dex in selectedGame.dexes"
            :key="dex.id"
            @click="selectDex(dex)"
            :class="[
              'px-5 py-2 text-sm font-semibold rounded-t-lg transition-colors',
              selectedDex?.id === dex.id
                ? 'bg-gray-100 text-red-600'
                : 'text-white/80 hover:text-white hover:bg-red-700'
            ]"
          >
            {{ dex.name }}
            <span class="ml-1 text-xs opacity-60">({{ dex.total }})</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Controls bar -->
    <div class="max-w-4xl mx-auto px-4 py-3 flex items-center gap-3">

      <!-- Search -->
      <div class="relative flex-1 max-w-xs">
        <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
          fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          v-model="search"
          type="text"
          placeholder="Search…"
          class="w-full pl-8 pr-8 py-1.5 text-sm bg-white border border-gray-200 rounded-lg shadow-sm outline-none focus:ring-2 focus:ring-red-400 focus:border-transparent"
        />
        <button
          v-if="search"
          @click="search = ''"
          class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >✕</button>
      </div>

      <!-- Progress bar -->
      <div class="flex items-center gap-2 flex-1 min-w-0">
        <div class="flex-1 bg-gray-200 rounded-full h-2.5 overflow-hidden">
          <div
            class="h-full bg-green-500 rounded-full transition-all duration-300"
            :style="{ width: progressPct + '%' }"
          />
        </div>
        <span class="text-xs text-gray-500 whitespace-nowrap">
          {{ caughtCount }} / {{ baseList.length }} caught
        </span>
      </div>

      <!-- Hide caught toggle -->
      <label class="flex items-center gap-2 cursor-pointer flex-shrink-0">
        <div
          @click="hideCaught = !hideCaught"
          :class="[
            'relative w-10 h-5 rounded-full transition-colors cursor-pointer',
            hideCaught ? 'bg-red-500' : 'bg-gray-300'
          ]"
        >
          <div :class="[
            'absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform',
            hideCaught ? 'translate-x-5' : 'translate-x-0.5'
          ]" />
        </div>
        <span class="text-sm text-gray-600 select-none">Hide caught</span>
      </label>

      <!-- Hide forms toggle -->
      <label class="flex items-center gap-2 cursor-pointer flex-shrink-0">
        <div
          @click="hideForms = !hideForms"
          :class="[
            'relative w-10 h-5 rounded-full transition-colors cursor-pointer',
            hideForms ? 'bg-blue-500' : 'bg-gray-300'
          ]"
        >
          <div :class="[
            'absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform',
            hideForms ? 'translate-x-5' : 'translate-x-0.5'
          ]" />
        </div>
        <span class="text-sm text-gray-600 select-none">Hide forms</span>
      </label>
    </div>

    <!-- Table -->
    <div class="max-w-4xl mx-auto px-4 pb-10">
      <div class="bg-white rounded-xl shadow overflow-hidden">

        <div v-if="loading" class="flex justify-center items-center py-16 text-gray-400 gap-2">
          <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          Loading…
        </div>

        <table v-else class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b text-xs font-semibold text-gray-400 uppercase tracking-wider">
              <th class="px-3 py-2.5 text-right">#NAT</th>
              <th class="px-3 py-2.5 text-right">#{{ selectedDex?.col_label }}</th>
              <th class="px-2 py-2.5 w-12"></th>
              <th class="px-3 py-2.5 text-left">Name</th>
              <th class="px-3 py-2.5 text-left">Types</th>
              <th class="px-3 py-2.5 text-center">Caught</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in filtered"
              :key="p.id"
              :class="['border-b last:border-0 transition-colors', p.caught ? 'bg-green-50' : 'hover:bg-gray-50']"
            >
              <td class="px-3 py-1.5 text-right text-gray-400 text-xs tabular-nums">{{ p.nac }}</td>
              <td class="px-3 py-1.5 text-right text-gray-400 text-xs tabular-nums">{{ p.dex_num }}</td>
              <td class="px-1 py-1 w-12 text-center">
                <img v-if="p.icon_url" :src="p.icon_url" :alt="p.name"
                  class="w-10 h-10 object-contain inline-block" loading="lazy" />
              </td>
              <td class="px-3 py-1.5 font-medium group"
                :class="p.caught ? 'text-gray-400 line-through' : 'text-gray-800'">
                {{ p.name }}
                <a
                  :href="'https://www.wikidex.net/wiki/' + encodeURIComponent(p.name.replace(/ /g, '_'))"
                  target="_blank"
                  rel="noopener"
                  class="opacity-0 group-hover:opacity-40 hover:!opacity-100 transition-opacity ml-1 inline-block align-middle"
                  @click.stop
                >
                  <svg class="w-3 h-3 inline" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-8.5M19 5l-7 7m0-5h5v5"/>
                  </svg>
                </a>
              </td>
              <td class="px-3 py-1.5">
                <div class="flex gap-1 flex-wrap">
                  <span v-if="p.tipo1"
                    :style="{ backgroundColor: TYPE_COLORS[p.tipo1] || '#aaa' }"
                    class="px-2 py-0.5 rounded text-white text-xs font-semibold">
                    {{ p.tipo1 }}
                  </span>
                  <span v-if="p.tipo2"
                    :style="{ backgroundColor: TYPE_COLORS[p.tipo2] || '#aaa' }"
                    class="px-2 py-0.5 rounded text-white text-xs font-semibold">
                    {{ p.tipo2 }}
                  </span>
                </div>
              </td>
              <td class="px-3 py-1.5 text-center">
                <input type="checkbox" :checked="!!p.caught" @change="toggleCaught(p)"
                  class="w-4 h-4 cursor-pointer accent-green-500 rounded" />
              </td>
            </tr>

            <tr v-if="filtered.length === 0">
              <td colspan="6" class="text-center py-10 text-gray-400">
                <template v-if="search">No results for "{{ search }}"</template>
                <template v-else-if="hideCaught">All caught! 🎉</template>
                <template v-else>No Pokémon to show.</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const TYPE_COLORS = {
  'Normal':    '#A8A878', 'Fuego':     '#F08030', 'Agua':      '#6890F0',
  'Planta':    '#78C850', 'Eléctrico': '#F8D030', 'Hielo':     '#98D8D8',
  'Pelea':     '#C03028', 'Lucha':     '#C03028', 'Veneno':    '#A040A0',
  'Tierra':    '#E0C068', 'Volador':   '#A890F0', 'Psíquico':  '#F85888',
  'Bicho':     '#A8B820', 'Roca':      '#B8A038', 'Fantasma':  '#705898',
  'Dragón':    '#7038F8', 'Siniestro': '#705848', 'Acero':     '#B8B8D0',
  'Hada':      '#EE99AC',
}

// ── State ──────────────────────────────────────────────────────────────────────
const games            = ref([])
const selectedGameSlug = ref(null)
const selectedDex      = ref(null)
const pokemon          = ref([])
const loading          = ref(false)
const gameDropdownOpen = ref(false)
const gameDropdownRef  = ref(null)
const hideCaught       = ref(sessionStorage.getItem('hideCaught') === 'true')
const hideForms        = ref(sessionStorage.getItem('hideForms') === 'true')
const search           = ref(sessionStorage.getItem('search') ?? '')

// ── Derived ────────────────────────────────────────────────────────────────────
const selectedGame = computed(() =>
  games.value.find(g => g.slug === selectedGameSlug.value) ?? null
)

const filtered = computed(() => {
  let list = baseList.value
  if (hideCaught.value) list = list.filter(p => !p.caught)
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(p => p.name?.toLowerCase().includes(q))
  }
  return list
})

const baseList = computed(() => {
  if (!hideForms.value) return pokemon.value
  const seen = new Set()
  return pokemon.value.filter(p => {
    const key = p.nac || p.dex_num
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
})

const caughtCount = computed(() => baseList.value.filter(p => p.caught).length)

const progressPct = computed(() =>
  baseList.value.length ? Math.round((caughtCount.value / baseList.value.length) * 100) : 0
)

// ── Actions ────────────────────────────────────────────────────────────────────
async function loadGames() {
  const res = await fetch('/api/games')
  games.value = await res.json()
  if (!games.value.length) return

  const savedSlug  = localStorage.getItem('selectedGameSlug')
  const savedDexId = Number(sessionStorage.getItem('selectedDexId'))

  const game = games.value.find(g => g.slug === savedSlug) ?? games.value[0]
  selectedGameSlug.value = game.slug
  selectedDex.value = game.dexes.find(d => d.id === savedDexId) ?? game.dexes[0] ?? null
}

async function loadPokemon() {
  if (!selectedDex.value) return
  loading.value = true
  search.value = ''
  const res = await fetch(`/api/dexes/${selectedDex.value.id}/pokemon`)
  pokemon.value = await res.json()
  loading.value = false
}

function selectDex(dex) {
  selectedDex.value = dex
}

async function toggleCaught(p) {
  const newVal = !p.caught
  p.caught = newVal ? 1 : 0 // optimistic update

  // Keep dex tab count in sync
  const dex = selectedGame.value?.dexes.find(d => d.id === selectedDex.value?.id)
  if (dex) dex.caught += newVal ? 1 : -1

  await fetch(`/api/pokemon/${p.id}/caught`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ caught: newVal }),
  })
}

// ── Watchers ───────────────────────────────────────────────────────────────────
watch(hideCaught, v => sessionStorage.setItem('hideCaught', v))
watch(hideForms,  v => sessionStorage.setItem('hideForms',  v))
watch(search,     v => sessionStorage.setItem('search',     v))

watch(selectedGameSlug, (slug, oldSlug) => {
  localStorage.setItem('selectedGameSlug', slug)
  // Solo resetea el tab cuando el usuario cambia de juego, no durante la inicialización
  if (oldSlug && selectedGame.value) selectedDex.value = selectedGame.value.dexes[0] ?? null
})

watch(selectedDex, (dex) => {
  if (dex) sessionStorage.setItem('selectedDexId', dex.id)
  loadPokemon()
})

onMounted(() => {
  loadGames()
  document.addEventListener('click', (e) => {
    if (gameDropdownRef.value && !gameDropdownRef.value.contains(e.target)) {
      gameDropdownOpen.value = false
    }
  })
})
</script>
