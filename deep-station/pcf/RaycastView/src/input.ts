// Keyboard, mouse, and pointer-lock input. Listeners attach to the control's own elements only
// (the code component FAQ says the Window object isn't supported), so the view must have focus.

export const BIT = { fwd: 1, back: 2, left: 4, right: 8, run: 16, fire: 32, turnL: 64, turnR: 128 } as const;

const KEYMAP: Record<string, number> = {
    KeyW: BIT.fwd, ArrowUp: BIT.fwd,
    KeyS: BIT.back, ArrowDown: BIT.back,
    KeyA: BIT.left,
    KeyD: BIT.right,
    ShiftLeft: BIT.run, ShiftRight: BIT.run,
    ControlLeft: BIT.fire, ControlRight: BIT.fire,
    ArrowLeft: BIT.turnL, ArrowRight: BIT.turnR,
};

const MOUSE_DEG_PER_PX = 0.15;
const KEY_TURN_DEG_S = 180;
const DRAG_FIRE_PX = 6; // a press that moves less than this without pointer lock counts as a click (fire)

export class Input {
    keys = 0;
    yaw = 0;
    useSeq = 0;
    weaponReq = 0;
    weaponSeq = 0;
    menuSeq = 0;
    mapSeq = 0;
    stamp = 0;
    /** Set whenever an output changed; the control notifies the host at most 30 times a second. */
    dirty = true;
    locked = false;
    lockRefused = false;

    private held = 0;          // keyboard bits
    private mouseFire = false;
    private dragging = false;
    private dragDist = 0;
    private enabled = true;

    constructor(private root: HTMLElement, private surface: HTMLElement, private onGesture: () => void) {
        root.tabIndex = 0;
        root.addEventListener("keydown", this.onKeyDown);
        root.addEventListener("keyup", this.onKeyUp);
        root.addEventListener("blur", this.onBlur);
        surface.addEventListener("mousedown", this.onMouseDown);
        surface.addEventListener("mousemove", this.onMouseMove);
        surface.addEventListener("mouseup", this.onMouseUp);
        surface.addEventListener("mouseleave", this.onMouseUp);
        surface.addEventListener("wheel", this.onWheel, { passive: false });
        surface.addEventListener("contextmenu", e => e.preventDefault());
        const doc = root.ownerDocument;
        doc.addEventListener("pointerlockchange", this.onLockChange);
        doc.addEventListener("pointerlockerror", this.onLockError);
    }

    destroy() {
        const r = this.root, s = this.surface, doc = r.ownerDocument;
        r.removeEventListener("keydown", this.onKeyDown);
        r.removeEventListener("keyup", this.onKeyUp);
        r.removeEventListener("blur", this.onBlur);
        s.removeEventListener("mousedown", this.onMouseDown);
        s.removeEventListener("mousemove", this.onMouseMove);
        s.removeEventListener("mouseup", this.onMouseUp);
        s.removeEventListener("mouseleave", this.onMouseUp);
        s.removeEventListener("wheel", this.onWheel);
        doc.removeEventListener("pointerlockchange", this.onLockChange);
        doc.removeEventListener("pointerlockerror", this.onLockError);
        if (doc.pointerLockElement === s) doc.exitPointerLock();
    }

    setEnabled(on: boolean) {
        if (on === this.enabled) return;
        this.enabled = on;
        if (!on) {
            this.held = 0;
            this.mouseFire = false;
            this.refreshKeys();
            const doc = this.root.ownerDocument;
            if (doc.pointerLockElement === this.surface) doc.exitPointerLock();
        }
    }

    /** Called every animation frame: applies key turning. */
    update(dtSec: number) {
        if (!this.enabled) return;
        const t = (this.held & BIT.turnR ? 1 : 0) - (this.held & BIT.turnL ? 1 : 0);
        if (t !== 0) {
            const rate = KEY_TURN_DEG_S * (this.held & BIT.run ? 1.5 : 1);
            this.turn(t * rate * dtSec);
        }
    }

    turn(deg: number) {
        this.yaw = ((this.yaw + deg) % 360 + 360) % 360;
        this.dirty = true;
    }

    private bump() {
        this.stamp = Math.floor(performance.now()) % 1000000000;
        this.dirty = true;
    }

    private refreshKeys() {
        const k = this.held | (this.mouseFire ? BIT.fire : 0);
        if (k !== this.keys) { this.keys = k; this.bump(); }
    }

    private onKeyDown = (e: KeyboardEvent) => {
        this.onGesture();
        if (!this.enabled) {
            if (e.code === "Escape") { this.menuSeq++; this.bump(); e.preventDefault(); }
            return;
        }
        const bit = KEYMAP[e.code];
        if (bit) { this.held |= bit; this.refreshKeys(); e.preventDefault(); return; }
        if (e.repeat) { e.preventDefault(); return; }
        switch (e.code) {
            case "KeyE": case "Space": this.useSeq++; this.bump(); break;
            case "Digit1": case "Digit2": case "Digit3": case "Digit4": case "Digit5":
                this.weaponReq = e.code.charCodeAt(5) - 48; this.weaponSeq++; this.bump(); break;
            case "Escape": this.menuSeq++; this.bump(); break;
            case "Tab": this.mapSeq++; this.bump(); break;
            default: return;
        }
        e.preventDefault();
    };

    private onKeyUp = (e: KeyboardEvent) => {
        const bit = KEYMAP[e.code];
        if (bit) { this.held &= ~bit; this.refreshKeys(); e.preventDefault(); }
    };

    private onBlur = () => { this.held = 0; this.mouseFire = false; this.refreshKeys(); };

    private onMouseDown = (e: MouseEvent) => {
        this.onGesture();
        this.root.focus({ preventScroll: true });
        if (!this.enabled) return;
        if (this.locked) {
            if (e.button === 0) { this.mouseFire = true; this.refreshKeys(); }
            return;
        }
        this.dragging = true;
        this.dragDist = 0;
        if (!this.lockRefused && this.surface.requestPointerLock) {
            try {
                const p = this.surface.requestPointerLock() as unknown;
                if (p && typeof (p as Promise<void>).catch === "function") (p as Promise<void>).catch(() => this.onLockError());
            } catch { this.onLockError(); }
        }
    };

    private onMouseMove = (e: MouseEvent) => {
        if (!this.enabled) return;
        if (this.locked) { this.turn(e.movementX * MOUSE_DEG_PER_PX); return; }
        if (this.dragging) { this.dragDist += Math.abs(e.movementX); this.turn(e.movementX * MOUSE_DEG_PER_PX * 1.5); }
    };

    private onMouseUp = (e: MouseEvent) => {
        if (this.locked) {
            if (e.type === "mouseup" && e.button === 0) { this.mouseFire = false; this.refreshKeys(); }
            return;
        }
        if (this.dragging && e.type === "mouseup" && this.dragDist < DRAG_FIRE_PX && this.lockRefused) {
            // fallback mode: a click without a drag is a single shot
            this.mouseFire = true; this.refreshKeys();
            setTimeout(() => { this.mouseFire = false; this.refreshKeys(); }, 120);
        }
        this.dragging = false;
    };

    private onWheel = (e: WheelEvent) => {
        if (!this.enabled) return;
        e.preventDefault();
        const cur = this.weaponReq || 2;
        this.weaponReq = ((cur - 1 + (e.deltaY > 0 ? 1 : 4)) % 5) + 1;
        this.weaponSeq++;
        this.bump();
    };

    private onLockChange = () => {
        this.locked = this.root.ownerDocument.pointerLockElement === this.surface;
        this.dragging = false;
        if (!this.locked) { this.mouseFire = false; this.refreshKeys(); }
    };

    private onLockError = () => { this.lockRefused = true; this.locked = false; };
}
