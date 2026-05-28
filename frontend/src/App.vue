<template>
  <div class="app-page">
    <header class="app-header">
      <div>
        <p class="eyebrow">Dataset Management</p>
        <h1>数据集管理</h1>
      </div>
    </header>

    <nav class="step-tabs" aria-label="流程步骤">
      <button
        v-for="step in workflowSteps"
        :key="step.id"
        class="step-tab"
        type="button"
        :class="{ active: currentStep === step.id }"
        :disabled="step.disabled || (step.id === 2 && !canEnterStepTwo)"
        @click="goToStep(step.id)"
      >
        <span class="step-index">{{ step.id }}</span>
        <span>{{ step.label }}</span>
      </button>
    </nav>

    <main v-if="currentStep === 1" class="app-shell">
      <FileSystemTree
        :root-node="rootNode"
        :selected-path="activePath"
        title="文件系统"
        loading-message="正在加载根目录..."
        show-add-button
        :add-disabled="!activePath || activePathAlreadySelected"
        :filter-loader="fetchFilteredChildren"
        @refresh="reloadRoot"
        @select="selectPath"
        @toggle="toggleNode"
        @load-more="loadMoreChildren"
        @add-node="addNodePath"
        @add-current="addSelectedPath"
      />

      <div class="step-right-column">
        <SelectedList
          :items="selectedPaths"
          :checked-count="checkedSelectedPaths.length"
          :total-count="selectedPaths.length"
          title="已选择路径"
          summary-label="paths"
          empty-message="从左侧选择文件或文件夹。&#10;Select files or folders from the left."
          show-toolbar
          @update-checked="setPathChecked"
          @toggle-all="setAllChecked"
          @delete="removeSelectedItem"
          @delete-all="deleteAllSelectedPaths"
        />

        <footer class="workflow-actions">
          <span></span>
          <button class="small-button primary-button" type="button" :disabled="!canEnterStepTwo" @click="enterStepTwo">
            Next
          </button>
        </footer>
      </div>
    </main>

    <main v-else class="step-two-shell">
      <div class="step-two-left">
        <SelectedList
          :items="checkedSelectedPaths"
          :checked-count="checkedSelectedPaths.length"
          :total-count="selectedPaths.length"
          :active-value="activeWorkflowPath"
          eyebrow="Selected"
          title="已选择路径"
          summary-label="paths"
          empty-message="暂无已勾选路径，请返回第一步勾选。"
          :show-delete-button="false"
          @update-checked="setPathChecked"
          @select="selectWorkflowPath"
        />

        <FileSystemTree
          :root-node="workflowRootNode"
          :selected-path="workflowTreeSelectedPath"
          eyebrow="Path Files"
          title="文件浏览"
          :empty-message="workflowTreeMessage"
          loading-message="正在加载当前路径..."
          refresh-label="刷新当前路径"
          :refresh-disabled="!workflowRootNode"
          show-root-node
          :filter-loader="fetchFilteredChildren"
          @refresh="reloadWorkflowRoot"
          @select="selectWorkflowTreePath"
          @toggle="toggleNode"
          @load-more="loadMoreChildren"
          @add-node="selectWorkflowTreePath"
        />
      </div>

      <div class="step-right-column">
        <section class="panel feature-panel">
          <header class="panel-header">
            <div>
              <p class="eyebrow">Actions</p>
              <h2>功能栏</h2>
            </div>
          </header>

          <div class="feature-placeholder">
            <h3>后续步骤与操作将在这里补充</h3>
            <p>当前页面已预留右侧功能区，后续可以接入不同步骤的参数配置、执行按钮或结果展示。</p>
          </div>
        </section>

        <footer class="workflow-actions">
          <span></span>
          <div class="workflow-action-buttons">
            <button class="small-button" type="button" @click="currentStep = 1">Back</button>
            <button class="small-button primary-button" type="button" disabled>Next</button>
          </div>
        </footer>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import FileSystemTree from "./components/FileSystemTree.vue";
import SelectedList from "./components/SelectedList.vue";

const filesystemRoot = "/";
const directoryPageSize = 20;
const currentStep = ref(1);
const activePath = ref("");
const activeNode = ref(null);
const selectedPaths = ref([]);
const activeWorkflowPath = ref("");
const workflowRootNode = ref(null);
const workflowTreeSelectedPath = ref("");
const workflowTreeMessage = ref("请先在上方选择一条路径。");
const rootNode = ref(createTreeNode({
  name: "/",
  path: filesystemRoot,
  type: "directory",
  hasChildren: true,
}));

const workflowSteps = [
  { id: 1, label: "选择路径" },
  { id: 2, label: "配置操作" },
  { id: 3, label: "后续步骤", disabled: true },
];

const checkedSelectedPaths = computed(() => {
  return selectedPaths.value.filter((item) => item.checked);
});

const activePathAlreadySelected = computed(() => {
  return selectedPaths.value.some((item) => item.path === activePath.value);
});

const canEnterStepTwo = computed(() => {
  return checkedSelectedPaths.value.length > 0;
});

function createTreeNode(node) {
  return {
    ...node,
    expanded: false,
    loading: false,
    loadingMore: false,
    error: "",
    children: [],
    childrenLoaded: node.childrenLoaded ?? false,
    childrenOffset: node.childrenOffset ?? 0,
    hasMoreChildren: node.hasMoreChildren ?? false,
  };
}

async function fetchChildren(path, offset = 0, filter = "") {
  const params = new URLSearchParams({
    path,
    offset: String(offset),
    limit: String(directoryPageSize),
  });
  if (filter) {
    params.set("filter", filter);
  }

  const response = await fetch(`/api/tree?${params.toString()}`);
  if (!response.ok) {
    const fallback = `读取失败：${response.status}`;
    const data = await response.json().catch(() => ({ detail: fallback }));
    throw new Error(data.detail || fallback);
  }
  return response.json();
}

async function fetchFilteredChildren(path, filter) {
  const children = [];
  let offset = 0;
  let hasMore = true;

  while (hasMore) {
    const data = await fetchChildren(path, offset, filter);
    children.push(...data.children.map(createTreeNode));
    offset = data.offset + data.children.length;
    hasMore = data.hasMore && data.children.length > 0;
  }

  return children;
}

async function loadChildren(node, force = false) {
  if (node.type !== "directory" || node.loading) {
    return;
  }

  if (node.childrenLoaded && !force) {
    return;
  }

  node.loading = true;
  node.error = "";

  try {
    const data = await fetchChildren(node.path, force ? 0 : node.childrenOffset);
    node.children = data.children.map(createTreeNode);
    node.childrenOffset = data.offset + data.children.length;
    node.hasMoreChildren = data.hasMore;
    node.childrenLoaded = true;
  } catch (error) {
    node.error = error.message;
  } finally {
    node.loading = false;
  }
}

async function loadMoreChildren(node) {
  if (node.type !== "directory" || node.loadingMore || !node.hasMoreChildren) {
    return;
  }

  node.loadingMore = true;
  node.error = "";

  try {
    const data = await fetchChildren(node.path, node.childrenOffset);
    node.children.push(...data.children.map(createTreeNode));
    node.childrenOffset = data.offset + data.children.length;
    node.hasMoreChildren = data.hasMore;
  } catch (error) {
    node.error = error.message;
  } finally {
    node.loadingMore = false;
  }
}

async function toggleNode(node) {
  if (node.type !== "directory") {
    return;
  }

  node.expanded = !node.expanded;
  if (node.expanded) {
    await loadChildren(node);
  }
}

function selectPath(node) {
  activePath.value = node.path;
  activeNode.value = node;
}

function addSelectedPath() {
  if (activePath.value && !activePathAlreadySelected.value) {
    selectedPaths.value.push({
      name: activeNode.value?.name || activePath.value,
      path: activePath.value,
      type: activeNode.value?.type || "directory",
      checked: true,
    });
  }
}

function addNodePath(node) {
  selectPath(node);
  addSelectedPath();
}

function removeSelectedPath(path) {
  selectedPaths.value = selectedPaths.value.filter((item) => item.path !== path);
  if (activeWorkflowPath.value === path) {
    const nextPath = checkedSelectedPaths.value[0];
    if (nextPath) {
      selectWorkflowPath(nextPath);
    } else {
      resetWorkflowSelection();
    }
  }
}

function removeSelectedItem(item) {
  removeSelectedPath(item.path);
}

function resetWorkflowSelection(message = "请先在第一步选择路径。") {
  activeWorkflowPath.value = "";
  workflowRootNode.value = null;
  workflowTreeSelectedPath.value = "";
  workflowTreeMessage.value = message;
}

function deleteAllSelectedPaths() {
  const confirmed = window.confirm("确认删除所有已选择路径吗？");
  if (!confirmed) {
    return;
  }

  selectedPaths.value = [];
  resetWorkflowSelection();
  currentStep.value = 1;
}

function syncWorkflowSelection() {
  if (currentStep.value !== 2) {
    return;
  }

  const activeItem = checkedSelectedPaths.value.find((item) => item.path === activeWorkflowPath.value);
  if (activeItem) {
    return;
  }

  const nextPath = checkedSelectedPaths.value[0];
  if (nextPath) {
    selectWorkflowPath(nextPath);
    return;
  }

  resetWorkflowSelection("请返回第一步勾选至少一条路径。");
  currentStep.value = 1;
}

function setPathChecked(item, checked) {
  item.checked = checked;
  syncWorkflowSelection();
}

function setAllChecked(checked) {
  selectedPaths.value.forEach((item) => {
    item.checked = checked;
  });
  syncWorkflowSelection();
}

async function reloadRoot() {
  rootNode.value.childrenLoaded = false;
  rootNode.value.expanded = true;
  await loadChildren(rootNode.value, true);
}

async function goToStep(stepId) {
  if (stepId === 1) {
    currentStep.value = 1;
    return;
  }

  if (stepId === 2 && canEnterStepTwo.value) {
    await enterStepTwo();
  }
}

async function enterStepTwo() {
  if (!canEnterStepTwo.value) {
    return;
  }

  currentStep.value = 2;
  const selectedItem = checkedSelectedPaths.value.find((item) => item.path === activeWorkflowPath.value)
    || checkedSelectedPaths.value[0];
  await selectWorkflowPath(selectedItem);
}

async function selectWorkflowPath(item) {
  activeWorkflowPath.value = item.path;
  workflowTreeSelectedPath.value = item.path;

  const itemType = item.type || "directory";

  if (itemType !== "directory") {
    workflowRootNode.value = null;
    workflowTreeMessage.value = "所选路径不是目录，无法展开子文件系统。";
    return;
  }

  workflowRootNode.value = createTreeNode({
    name: item.name || item.path,
    path: item.path,
    type: "directory",
    hasChildren: true,
  });
  workflowRootNode.value.expanded = true;
  workflowTreeMessage.value = "";
  await loadChildren(workflowRootNode.value, true);
}

function selectWorkflowTreePath(node) {
  workflowTreeSelectedPath.value = node.path;
}

async function reloadWorkflowRoot() {
  if (!workflowRootNode.value) {
    return;
  }

  workflowRootNode.value.childrenLoaded = false;
  workflowRootNode.value.expanded = true;
  await loadChildren(workflowRootNode.value, true);
}

onMounted(async () => {
  rootNode.value.expanded = true;
  await loadChildren(rootNode.value);
});
</script>
