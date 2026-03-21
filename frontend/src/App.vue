<template>
  <div :class="['min-h-screen', darkMode ? 'dark' : '']">
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors">

    <!-- Header -->
    <header class="bg-red-600 shadow-lg">
      <div class="max-w-4xl mx-auto px-4 pt-4 pb-0">

        <!-- Game title + selector -->
        <div class="flex items-center gap-3 mb-3">
          <div class="w-8 h-8 rounded-full bg-white border-4 border-gray-800 flex-shrink-0" />
          <div class="relative flex-1" ref="gameDropdownRef">
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
                class="absolute top-full left-0 mt-2 bg-white dark:bg-gray-800 rounded-xl shadow-xl z-50 overflow-hidden min-w-56"
              >
                <button
                  v-for="g in games"
                  :key="g.slug"
                  @click="selectedGameSlug = g.slug; gameDropdownOpen = false"
                  :class="[
                    'w-full text-left px-4 py-3 text-sm font-medium transition-colors',
                    g.slug === selectedGameSlug
                      ? 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                  ]"
                >
                  {{ g.name }}
                  <span class="block text-xs text-gray-400 dark:text-gray-500 font-normal">{{ g.year }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Dark mode toggle -->
          <button
            @click="darkMode = !darkMode"
            class="flex-shrink-0 w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 transition-colors flex items-center justify-center text-white"
          >
            <svg v-if="darkMode" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
          </button>
        </div>

        <!-- Dex tabs — desktop -->
        <div class="hidden sm:flex gap-1 overflow-x-auto" v-if="selectedGame">
          <button
            v-for="dex in selectedGame.dexes"
            :key="dex.id"
            @click="selectDex(dex)"
            :class="[
              'px-5 py-2 text-sm font-semibold rounded-t-lg transition-colors whitespace-nowrap flex-shrink-0',
              selectedDex?.id === dex.id
                ? 'bg-gray-100 dark:bg-gray-900 text-red-600 dark:text-white'
                : 'text-white/80 hover:text-white hover:bg-red-700'
            ]"
          >
            {{ dex.name }}
            <span class="ml-1 text-xs opacity-60">({{ dexTotal(dex) }})</span>
          </button>
        </div>

        <!-- Dex selector — mobile -->
        <div class="sm:hidden px-1 pb-2" v-if="selectedGame">
          <select
            :value="selectedDex?.id"
            @change="selectDex(selectedGame.dexes.find(d => d.id === $event.target.value))"
            class="w-full rounded-lg px-3 py-2 text-sm font-semibold bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
          >
            <option
              v-for="dex in selectedGame.dexes"
              :key="dex.id"
              :value="dex.id"
              class="text-gray-900"
            >
              {{ dex.name }} ({{ dexTotal(dex) }})
            </option>
          </select>
        </div>
      </div>
    </header>

    <!-- Controls bar -->
    <div class="max-w-4xl mx-auto px-4 py-3 flex flex-col gap-2">

      <!-- Row 1: search + export/import -->
      <div class="flex items-center gap-2">
        <div class="relative flex-1">
          <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
            fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="search"
            type="text"
            placeholder="Search…"
            class="w-full pl-8 pr-8 py-1.5 text-sm bg-white dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm outline-none focus:ring-2 focus:ring-red-400 focus:border-transparent"
          />
          <button
            v-if="search"
            @click="search = ''"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >✕</button>
        </div>

        <template v-if="STATIC">
          <button @click="exportData" title="Export progress"
            class="flex-shrink-0 p-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
          </button>
          <label title="Import progress"
            class="flex-shrink-0 p-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            <input type="file" accept=".json" class="hidden" @change="importData" />
          </label>
        </template>
      </div>

      <!-- Row 2: progress + toggles -->
      <div class="flex items-center gap-3 flex-wrap">

        <!-- Progress bar -->
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
            <div class="h-full bg-green-500 rounded-full transition-all duration-300" :style="{ width: progressPct + '%' }" />
          </div>
          <span class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
            {{ caughtCount }} / {{ baseList.length }} caught
          </span>
        </div>

        <!-- Hide caught toggle -->
        <label class="flex items-center gap-1.5 cursor-pointer flex-shrink-0">
          <div @click="hideCaught = !hideCaught"
            :class="['relative w-9 h-5 rounded-full transition-colors cursor-pointer', hideCaught ? 'bg-red-500' : 'bg-gray-300 dark:bg-gray-600']">
            <div :class="['absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform', hideCaught ? 'translate-x-4' : 'translate-x-0.5']" />
          </div>
          <span class="text-xs text-gray-600 dark:text-gray-400 select-none">Hide caught</span>
        </label>

        <!-- Hide forms toggle -->
        <label class="flex items-center gap-1.5 cursor-pointer flex-shrink-0">
          <div @click="hideForms = !hideForms"
            :class="['relative w-9 h-5 rounded-full transition-colors cursor-pointer', hideForms ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600']">
            <div :class="['absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform', hideForms ? 'translate-x-4' : 'translate-x-0.5']" />
          </div>
          <span class="text-xs text-gray-600 dark:text-gray-400 select-none">Hide forms</span>
        </label>
      </div>
    </div>

    <!-- Table -->
    <div class="max-w-4xl mx-auto px-4 pb-10">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">

        <div v-if="loading" class="flex justify-center items-center py-16 text-gray-400 gap-2">
          <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          Loading…
        </div>

        <table v-else class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 dark:bg-gray-700/50 border-b dark:border-gray-700 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              <th class="px-3 py-2.5 text-right hidden sm:table-cell">#NAT</th>
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
              :class="['border-b dark:border-gray-700 last:border-0 transition-colors', p.caught ? 'bg-green-50 dark:bg-green-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-700/40', fadingOut.has(p.id) ? 'caught-fade-out' : '']"
            >
              <td class="px-3 py-1.5 text-right text-gray-400 dark:text-gray-500 text-xs tabular-nums hidden sm:table-cell">{{ p.nac }}</td>
              <td class="px-3 py-1.5 text-right text-gray-400 dark:text-gray-500 text-xs tabular-nums">{{ p.dex_num }}</td>
              <td class="px-1 py-1 w-12 text-center">
                <img v-if="p.icon_url" :src="p.icon_url" :alt="p.name"
                  class="w-10 h-10 object-contain inline-block" loading="lazy" />
              </td>
              <td class="px-3 py-1.5 font-medium group"
                :class="p.caught ? 'text-gray-400 dark:text-gray-600 line-through' : 'text-gray-800 dark:text-gray-100'">
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
                <button @click="toggleCaught(p)" :class="['inline-flex items-center justify-center w-8 h-8 rounded-full', catching.has(p.id) ? 'pokeball-catch' : 'transition-transform hover:scale-110 active:scale-95']">
                  <svg viewBox="0 0 100 100" class="w-7 h-7">
                    <template v-if="p.caught">
                      <circle cx="50" cy="50" r="47" fill="#dc2626" stroke="#1f2937" stroke-width="5"/>
                      <rect x="3" y="45" width="94" height="10" fill="#1f2937"/>
                      <circle cx="50" cy="50" r="15" fill="white" stroke="#1f2937" stroke-width="5"/>
                      <circle cx="50" cy="50" r="7" fill="#1f2937"/>
                    </template>
                    <template v-else>
                      <circle cx="50" cy="50" r="47" fill="none" stroke="#d1d5db" stroke-width="5"/>
                      <path d="M3 50 Q3 3 50 3" stroke="#d1d5db" stroke-width="5" fill="none"/>
                      <path d="M50 3 Q97 3 97 50" stroke="#d1d5db" stroke-width="5" fill="none"/>
                      <rect x="3" y="45" width="94" height="10" fill="#d1d5db"/>
                      <circle cx="50" cy="50" r="15" fill="none" stroke="#d1d5db" stroke-width="5"/>
                      <circle cx="50" cy="50" r="7" fill="#d1d5db"/>
                    </template>
                  </svg>
                </button>
              </td>
            </tr>

            <tr v-if="filtered.length === 0">
              <td colspan="6" class="text-center py-10 text-gray-400 dark:text-gray-600">
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
    <!-- Undo toast -->
    <transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div
        v-if="undoToast"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 bg-gray-900 dark:bg-gray-700 text-white px-4 py-3 rounded-xl shadow-xl"
      >
        <span class="text-sm">
          <span class="font-semibold">{{ undoToast.pokemon.name }}</span>
          {{ undoToast.pokemon.caught ? ' caught' : ' uncaught' }}
        </span>
        <button
          @click="doUndo"
          class="text-sm font-bold text-red-400 hover:text-red-300 transition-colors"
        >Undo</button>
        <div class="w-16 h-1 bg-gray-600 rounded-full overflow-hidden">
          <div class="h-full bg-red-400 rounded-full" :style="{ width: undoProgress + '%', transition: 'width 3s linear' }" />
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const STATIC = import.meta.env.VITE_STATIC_MODE === 'true'

// ── Static mode helpers ────────────────────────────────────────────────────────
const GAME_FILES = {
  'legends-za':      () => import('./data/legends-za.json'),
  'legends-arceus':  () => import('./data/legends-arceus.json'),
  'scarlet-violet':  () => import('./data/scarlet-violet.json'),
  'sword-shield':    () => import('./data/sword-shield.json'),
  'bdsp':            () => import('./data/bdsp.json'),
  'lets-go':         () => import('./data/lets-go.json'),
}
const staticPokemonStore = {}

function staticKey(p) { return `${p.nac}||${p.name}` }

function staticCaughtSet(gameSlug, dexSlug) {
  const raw = localStorage.getItem(`pokedex:caught:${gameSlug}:${dexSlug}`)
  return new Set(raw ? JSON.parse(raw) : [])
}

function staticSaveCaught(gameSlug, dexSlug, set) {
  localStorage.setItem(`pokedex:caught:${gameSlug}:${dexSlug}`, JSON.stringify([...set]))
}

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
const undoToast        = ref(null)
const undoProgress     = ref(100)
const darkMode         = ref(localStorage.getItem('darkMode') === 'true')
const hideCaught       = ref(sessionStorage.getItem('hideCaught') === 'true')
const hideForms        = ref(sessionStorage.getItem('hideForms') === 'true')
const search           = ref(sessionStorage.getItem('search') ?? '')
const fadingOut        = ref(new Set())
const catching         = ref(new Set())
const dexStats         = ref({})

// ── Derived ────────────────────────────────────────────────────────────────────
const selectedGame = computed(() =>
  games.value.find(g => g.slug === selectedGameSlug.value) ?? null
)

const filtered = computed(() => {
  let list = baseList.value
  if (hideCaught.value) list = list.filter(p => !p.caught || fadingOut.value.has(p.id))
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

function dexTotal(dex) {
  if (dex.id === selectedDex.value?.id) return baseList.value.length
  if (!hideForms.value) return dex.total
  // modo estático: calcular desde store en memoria
  const list = staticPokemonStore[dex.id]
  if (list) {
    const seen = new Set()
    let count = 0
    for (const p of list) {
      const key = p.nac || p.dex_num
      if (!seen.has(key)) { seen.add(key); count++ }
    }
    return count
  }
  // modo servidor: usar stats pre-calculados al boot
  return dexStats.value[dex.id]?.total_no_forms ?? dex.total
}

const progressPct = computed(() =>
  baseList.value.length ? Math.round((caughtCount.value / baseList.value.length) * 100) : 0
)

// ── Actions ────────────────────────────────────────────────────────────────────
async function loadGames() {
  if (STATIC) {
    let dexId = 1
    const allData = await Promise.all(Object.values(GAME_FILES).map(f => f()))
    games.value = allData
      .map(m => m.default)
      .sort((a, b) => b.game.year - a.game.year || a.game.name.localeCompare(b.game.name))
      .map((data, gi) => {
        const dexes = data.dexes.map(dex => {
          const id = dexId++
          const caught = staticCaughtSet(data.game.slug, dex.slug)
          staticPokemonStore[id] = dex.pokemon.map((p, i) => ({
            id: id * 100000 + i, dex_id: id,
            nac: p.nac, dex_num: p.dex_num, name: p.name,
            tipo1: p.tipo1, tipo2: p.tipo2, icon_url: p.icon_url,
            caught: caught.has(staticKey(p)) ? 1 : 0,
          }))
          return {
            id, game_id: gi + 1, slug: dex.slug, name: dex.name, col_label: dex.col_label,
            total: dex.pokemon.length,
            caught: staticPokemonStore[id].filter(p => p.caught).length,
            _gameSlug: data.game.slug,
          }
        })
        return { id: gi + 1, slug: data.game.slug, name: data.game.name, year: data.game.year, dexes }
      })
  } else {
    const res = await fetch('/api/games')
    games.value = await res.json()
  }
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
  if (STATIC) {
    pokemon.value = staticPokemonStore[selectedDex.value.id] || []
  } else {
    const res = await fetch(`/api/dexes/${selectedDex.value.id}/pokemon`)
    pokemon.value = await res.json()
  }
  loading.value = false
}

function selectDex(dex) {
  selectedDex.value = dex
}

function toggleCaught(p) {
  // Commit any previous pending toast immediately
  if (undoToast.value && undoToast.value.pokemon.id !== p.id) {
    commitUndo(undoToast.value)
  }

  const prevCaught = p.caught
  const newVal = !p.caught
  p.caught = newVal ? 1 : 0

  if (newVal) {
    catching.value.add(p.id)
    catching.value = new Set(catching.value)
    setTimeout(() => {
      catching.value.delete(p.id)
      catching.value = new Set(catching.value)
    }, 850)
  }

  if (newVal && hideCaught.value) {
    fadingOut.value.add(p.id)
    fadingOut.value = new Set(fadingOut.value)
    setTimeout(() => {
      fadingOut.value.delete(p.id)
      fadingOut.value = new Set(fadingOut.value)
    }, 600)
  }

  const dex = selectedGame.value?.dexes.find(d => d.id === selectedDex.value?.id)
  if (dex) dex.caught += newVal ? 1 : -1

  if (undoToast.value) clearTimeout(undoToast.value.timer)

  // Save immediately — undo will make a second request to revert
  persistCaught(p)

  undoProgress.value = 100
  const timer = setTimeout(() => { undoToast.value = null }, 3000)
  undoToast.value = { pokemon: p, prevCaught, dex, timer }
  requestAnimationFrame(() => { undoProgress.value = 0 })
}

async function persistCaught(p) {
  if (STATIC) {
    const dex = selectedGame.value?.dexes.find(d => d.id === selectedDex.value?.id)
    const gameSlug = dex?._gameSlug ?? selectedGame.value?.slug
    const set = staticCaughtSet(gameSlug, dex?.slug)
    const key = staticKey(p)
    if (p.caught) set.add(key); else set.delete(key)
    staticSaveCaught(gameSlug, dex?.slug, set)
  } else {
    await fetch(`/api/pokemon/${p.id}/caught`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ caught: !!p.caught }),
    })
  }
}

function commitUndo(toast) {
  if (!toast) return
  if (undoToast.value?.timer === toast.timer) undoToast.value = null
  clearTimeout(toast.timer)
}

function doUndo() {
  if (!undoToast.value) return
  const { pokemon: p, prevCaught, dex, timer } = undoToast.value
  clearTimeout(timer)
  undoToast.value = null

  const wasCaught = !!p.caught
  p.caught = prevCaught
  if (dex) dex.caught += wasCaught ? -1 : 1
  fadingOut.value.delete(p.id)
  fadingOut.value = new Set(fadingOut.value)
  catching.value.delete(p.id)
  catching.value = new Set(catching.value)

  persistCaught(p)
}

function exportData() {
  const caught = {}
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    if (key.startsWith('pokedex:caught:')) {
      caught[key] = JSON.parse(localStorage.getItem(key))
    }
  }
  const blob = new Blob([JSON.stringify({ version: 1, exported: new Date().toISOString(), caught }, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `pokedex-progress-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(a.href)
}

async function importData(e) {
  const file = e.target.files[0]
  if (!file) return
  try {
    const text = await file.text()
    const { caught } = JSON.parse(text)
    if (!caught || typeof caught !== 'object') throw new Error()
    Object.entries(caught).forEach(([key, val]) => {
      if (key.startsWith('pokedex:caught:')) localStorage.setItem(key, JSON.stringify(val))
    })
    await loadGames()
    await loadPokemon()
  } catch {
    alert('Invalid file.')
  }
  e.target.value = ''
}

// ── Watchers ───────────────────────────────────────────────────────────────────
watch(darkMode,   v => localStorage.setItem('darkMode', v))
watch(hideCaught, v => sessionStorage.setItem('hideCaught', v))
watch(hideForms,  v => sessionStorage.setItem('hideForms',  v))
watch(search,     v => sessionStorage.setItem('search',     v))

watch(selectedGameSlug, (slug, oldSlug) => {
  localStorage.setItem('selectedGameSlug', slug)
  if (oldSlug && selectedGame.value) selectedDex.value = selectedGame.value.dexes[0] ?? null
})

watch(selectedDex, (dex) => {
  if (dex) sessionStorage.setItem('selectedDexId', dex.id)
  loadPokemon()
})

onMounted(() => {
  if (!STATIC) fetch('/api/dex-stats').then(r => r.json()).then(d => { dexStats.value = d })
  loadGames()
  document.addEventListener('click', (e) => {
    if (gameDropdownRef.value && !gameDropdownRef.value.contains(e.target)) {
      gameDropdownOpen.value = false
    }
  })
})
</script>
