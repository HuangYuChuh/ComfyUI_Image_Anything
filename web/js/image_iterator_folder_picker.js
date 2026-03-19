import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

const EXTENSION_NAME = "ComfyUI_Image_Anything.ImageIteratorFolderPicker";
const PICKER_ROUTE = "/image_anything/pick-folder";
const PICKER_WIDGET_KEY = "__imageAnythingFolderPickerWidget";
const NODE_PICKER_CONFIG = {
    ImageIterator: {
        pathWidget: "folder_path",
        buttonLabel: "Choose Folder",
        successMessage: "Folder path updated.",
        cancelledMessage: "Folder selection cancelled.",
        busyLabel: "Choosing folder...",
        directoryType: "input",
    },
    ImageSaver: {
        pathWidget: "save_path",
        buttonLabel: "Choose Save Folder",
        successMessage: "Save path updated.",
        cancelledMessage: "Folder selection cancelled.",
        busyLabel: "Choosing save folder...",
        directoryType: "output",
    },
};

let toastRoot = null;

function ensureToastRoot() {
    if (toastRoot && document.body.contains(toastRoot)) {
        return toastRoot;
    }

    toastRoot = document.createElement("div");
    toastRoot.className = "image-anything-folder-toast-root";

    Object.assign(toastRoot.style, {
        position: "fixed",
        top: "16px",
        right: "16px",
        zIndex: "10001",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        pointerEvents: "none",
    });

    document.body.appendChild(toastRoot);
    return toastRoot;
}

function showToast(message, tone = "info") {
    const root = ensureToastRoot();
    const toast = document.createElement("div");

    const accent =
        tone === "error"
            ? "var(--error-text, #ff8f8f)"
            : "var(--primary-bg, #236692)";

    Object.assign(toast.style, {
        minWidth: "280px",
        maxWidth: "420px",
        padding: "12px 14px",
        borderRadius: "10px",
        border: `1px solid ${accent}`,
        background: "var(--comfy-menu-bg, #353535)",
        color: "var(--fg-color, #fff)",
        boxShadow: "0 10px 24px rgba(0, 0, 0, 0.28)",
        fontSize: "13px",
        lineHeight: "1.45",
        opacity: "0",
        transform: "translateY(-6px)",
        transition: "opacity 160ms ease, transform 160ms ease",
        pointerEvents: "auto",
    });

    toast.textContent = message;
    root.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateY(0)";
    });

    window.setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-6px)";
        window.setTimeout(() => toast.remove(), 180);
    }, 3200);
}

function findWidget(node, widgetName) {
    return node.widgets?.find((widget) => widget.name === widgetName) ?? null;
}

function updateNodeLayout(node) {
    node.setSize([node.size[0], node.computeSize()[1]]);
    node.setDirtyCanvas(true, true);
}

async function openFolderPicker(node) {
    const config = NODE_PICKER_CONFIG[node.type];
    const folderPathWidget = config ? findWidget(node, config.pathWidget) : null;
    const pickerWidget = node[PICKER_WIDGET_KEY];

    if (!config || !folderPathWidget || !pickerWidget || pickerWidget.__imageAnythingBusy) {
        return;
    }

    const previousLabel = pickerWidget.name;
    pickerWidget.__imageAnythingBusy = true;
    pickerWidget.name = config.busyLabel;
    updateNodeLayout(node);

    try {
        const response = await api.fetchApi(PICKER_ROUTE, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                initial_path: typeof folderPathWidget.value === "string" ? folderPathWidget.value : "",
                directory_type: config.directoryType,
            }),
        });

        const payload = await response.json();

        if (!response.ok || payload.status === "error") {
            throw new Error(payload.message || "Failed to choose folder.");
        }

        if (payload.status === "cancelled") {
            showToast(config.cancelledMessage);
            return;
        }

        folderPathWidget.value = payload.path;
        if (typeof folderPathWidget.callback === "function") {
            folderPathWidget.callback(payload.path);
        }
        showToast(config.successMessage);
    } catch (error) {
        console.error("[ImageIterator] Folder picker failed.", error);
        showToast(
            error instanceof Error ? error.message : "Failed to choose folder.",
            "error"
        );
    } finally {
        pickerWidget.__imageAnythingBusy = false;
        pickerWidget.name = previousLabel;
        updateNodeLayout(node);
    }
}

function ensurePickerWidget(node) {
    const config = NODE_PICKER_CONFIG[node.type];
    if (!config || node[PICKER_WIDGET_KEY]) {
        return;
    }

    const pickerWidget = node.addWidget(
        "button",
        config.buttonLabel,
        null,
        () => openFolderPicker(node),
        {
            serialize: false,
        }
    );

    pickerWidget.__imageAnythingBusy = false;
    node[PICKER_WIDGET_KEY] = pickerWidget;
    updateNodeLayout(node);
}

app.registerExtension({
    name: EXTENSION_NAME,

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (!NODE_PICKER_CONFIG[nodeData.name]) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;

        nodeType.prototype.onNodeCreated = function() {
            const result = originalOnNodeCreated
                ? originalOnNodeCreated.apply(this, arguments)
                : undefined;

            ensurePickerWidget(this);
            return result;
        };
    },

    async nodeCreated(node) {
        ensurePickerWidget(node);
    },
});
