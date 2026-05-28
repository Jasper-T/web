<template>
  <section class="panel explorer-panel">
    <header class="panel-header">
      <div>
        <p class="eyebrow">{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
      </div>
      <div class="header-actions">
        <form class="tree-filter" role="search" @submit.prevent="applyFilter">
          <input
            v-model="filterText"
            class="tree-filter-input"
            type="search"
            placeholder="Filter files or folders"
            aria-label="Filter files or folders"
          />
          <button class="small-button tree-filter-button" type="submit" :disabled="isFiltering">
            <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 5h16l-6 7v5l-4 2v-7L4 5Z" fill="currentColor" />
            </svg>
            <span>{{ isFiltering ? "Filtering..." : "Filter" }}</span>
          </button>
          <button
            v-if="filterText || activeFilter"
            class="small-button"
            type="button"
            :disabled="isFiltering"
            @click="clearFilter"
          >
            Clear
          </button>
        </form>
        <button
          class="small-button icon-button"
          type="button"
          :aria-label="refreshLabel"
          :disabled="refreshDisabled"
          @click="$emit('refresh')"
        >
          <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M17.7 6.3A8 8 0 1 0 20 12h-2a6 6 0 1 1-1.76-4.24L13 11h8V3l-3.3 3.3Z"
              fill="currentColor"
            />
          </svg>
        </button>
        <button
          v-if="showAddButton"
          class="small-button icon-button"
          type="button"
          :aria-label="addLabel"
          :disabled="addDisabled"
          @click="$emit('add-current')"
        >
          <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M11 5h2v6h6v2h-6v6h-2v-6H5v-2h6V5Z" fill="currentColor" />
          </svg>
        </button>
      </div>
    </header>

    <div v-if="rootNode" class="tree-container">
      <p v-if="rootNode.error" class="tree-error root-tree-error">
        {{ rootNode.error }}
      </p>
      <div v-if="rootNode.loading" class="empty-state compact-empty-state">
        {{ loadingMessage }}
      </div>
      <div v-else-if="isFiltering" class="empty-state compact-empty-state">
        Filtering...
      </div>
      <div v-else-if="filterError" class="empty-state compact-empty-state">
        {{ filterError }}
      </div>
      <div v-else-if="activeFilter && !hasFilterResults" class="empty-state compact-empty-state">
        No matches found.
      </div>
      <ul v-else class="tree-list">
        <TreeNode
          v-if="showRootNode"
          :node="displayRootNode"
          :selected-path="selectedPath"
          :hide-load-more="isFilterActive"
          @select="$emit('select', $event)"
          @toggle="$emit('toggle', $event)"
          @load-more="$emit('load-more', $event)"
          @add="$emit('add-node', $event)"
        />
        <template v-else>
          <TreeNode
            v-for="child in displayChildren"
            :key="child.path"
            :node="child"
            :selected-path="selectedPath"
            :hide-load-more="isFilterActive"
            @select="$emit('select', $event)"
            @toggle="$emit('toggle', $event)"
            @load-more="$emit('load-more', $event)"
            @add="$emit('add-node', $event)"
          />
          <li v-if="rootNode.hasMoreChildren && !isFilterActive">
            <button
              class="tree-load-more"
              type="button"
              :disabled="rootNode.loadingMore"
              @click="$emit('load-more', rootNode)"
            >
              {{ rootNode.loadingMore ? "loading..." : "..." }}
            </button>
          </li>
        </template>
      </ul>
    </div>
    <div v-else class="empty-state compact-empty-state">
      {{ emptyMessage }}
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from "vue";
import TreeNode from "./TreeNode.vue";

const props = defineProps({
  rootNode: {
    type: Object,
    default: null,
  },
  selectedPath: {
    type: String,
    default: "",
  },
  eyebrow: {
    type: String,
    default: "File System",
  },
  title: {
    type: String,
    default: "File System",
  },
  emptyMessage: {
    type: String,
    default: "No content to display.",
  },
  loadingMessage: {
    type: String,
    default: "Loading...",
  },
  refreshLabel: {
    type: String,
    default: "Refresh",
  },
  addLabel: {
    type: String,
    default: "Add selected item",
  },
  refreshDisabled: {
    type: Boolean,
    default: false,
  },
  showAddButton: {
    type: Boolean,
    default: false,
  },
  addDisabled: {
    type: Boolean,
    default: false,
  },
  showRootNode: {
    type: Boolean,
    default: false,
  },
  filterLoader: {
    type: Function,
    default: null,
  },
});

defineEmits(["refresh", "select", "toggle", "load-more", "add-node", "add-current"]);

const filterText = ref("");
const activeFilter = ref("");
const isFiltering = ref(false);
const filterError = ref("");
const filteredChildrenByPath = ref(new Map());
let filterRequestId = 0;

const isFilterActive = computed(() => activeFilter.value.length > 0);

const displayRootNode = computed(() => {
  if (!props.rootNode || !isFilterActive.value) {
    return props.rootNode;
  }

  return filterNode(props.rootNode);
});

const displayChildren = computed(() => {
  if (!props.rootNode) {
    return [];
  }

  if (!isFilterActive.value) {
    return props.rootNode.children;
  }

  return getFilterCandidateChildren(props.rootNode).map(filterNode).filter(Boolean);
});

const hasFilterResults = computed(() => {
  if (!isFilterActive.value) {
    return true;
  }

  if (props.showRootNode) {
    return Boolean(displayRootNode.value);
  }

  return displayChildren.value.length > 0;
});

async function applyFilter() {
  const requestId = ++filterRequestId;
  isFiltering.value = true;
  filterError.value = "";
  const nextFilter = filterText.value.trim();
  await nextTick();

  try {
    const nextFilteredChildrenByPath = new Map();
    if (nextFilter && props.rootNode && props.filterLoader) {
      await loadFilteredBranches(props.rootNode, nextFilter, nextFilteredChildrenByPath, new Set());
    }

    if (requestId !== filterRequestId) {
      return;
    }

    filteredChildrenByPath.value = nextFilteredChildrenByPath;
    activeFilter.value = nextFilter;
  } catch (error) {
    if (requestId === filterRequestId) {
      filterError.value = error.message || "Filter failed.";
    }
  } finally {
    if (requestId === filterRequestId) {
      isFiltering.value = false;
    }
  }
}

function clearFilter() {
  filterText.value = "";
  applyFilter();
}

function filterNode(node) {
  const children = getFilterCandidateChildren(node).map(filterNode).filter(Boolean);
  const name = String(node.name ?? "");
  const matchesSelf = name.includes(activeFilter.value);

  if (!matchesSelf && children.length === 0) {
    return null;
  }

  return {
    ...node,
    sourceNode: node,
    children,
    expanded: node.expanded || children.length > 0,
    hasMoreChildren: false,
  };
}

async function loadFilteredBranches(node, filter, nextFilteredChildrenByPath, visitedPaths) {
  if (node.type !== "directory" || visitedPaths.has(node.path)) {
    return;
  }

  visitedPaths.add(node.path);
  nextFilteredChildrenByPath.set(node.path, await props.filterLoader(node.path, filter));

  for (const child of node.children ?? []) {
    if (child.type === "directory" && child.childrenLoaded) {
      await loadFilteredBranches(child, filter, nextFilteredChildrenByPath, visitedPaths);
    }
  }
}

function getFilterCandidateChildren(node) {
  if (!isFilterActive.value) {
    return node.children ?? [];
  }

  const childrenByPath = new Map();
  for (const child of node.children ?? []) {
    childrenByPath.set(child.path, child);
  }

  for (const child of filteredChildrenByPath.value.get(node.path) ?? []) {
    if (!childrenByPath.has(child.path)) {
      childrenByPath.set(child.path, child);
    }
  }

  return Array.from(childrenByPath.values());
}

onBeforeUnmount(() => {
  filterRequestId += 1;
});
</script>
