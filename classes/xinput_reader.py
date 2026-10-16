"""Lettura input controller Xbox tramite XInput (Windows API)."""

import ctypes
from ctypes import wintypes

from .config import XINPUT_GAMEPAD_A


class _XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ("wButtons", wintypes.WORD),
        ("bLeftTrigger", wintypes.BYTE),
        ("bRightTrigger", wintypes.BYTE),
        ("sThumbLX", wintypes.SHORT),
        ("sThumbLY", wintypes.SHORT),
        ("sThumbRX", wintypes.SHORT),
        ("sThumbRY", wintypes.SHORT),
    ]


class _XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ("dwPacketNumber", wintypes.DWORD),
        ("Gamepad", _XINPUT_GAMEPAD),
    ]


class XInputReader:
    """Legge lo stato dei controller Xbox tramite XInput (Windows)."""

    def __init__(self):
        self._dll = None
        self._state = _XINPUT_STATE()
        for dll_name in ("xinput1_4.dll", "xinput1_3.dll"):
            try:
                self._dll = ctypes.windll.LoadLibrary(dll_name)
                break
            except OSError:
                continue

    def get_state(self, player_index: int = 0):
        """Restituisce True se il controller e' connesso e carica lo stato interno."""
        if not self._dll:
            return False
        res = self._dll.XInputGetState(player_index, ctypes.byref(self._state))
        return res == 0

    def get_left_x(self, player_index: int = 0) -> float:
        """Restituisce l'asse X dello stick sinistro normalizzato in [-1.0, 1.0]."""
        if not self.get_state(player_index):
            return 0.0
        raw = self._state.Gamepad.sThumbLX
        val = raw / 32768.0
        return val

    def get_left_y(self, player_index: int = 0) -> float:
        """Restituisce l'asse Y dello stick sinistro normalizzato in [-1.0, 1.0]."""
        if not self.get_state(player_index):
            return 0.0
        raw = self._state.Gamepad.sThumbLY
        val = raw / 32768.0
        return val

    def get_right_trigger(self, player_index: int = 0) -> float:
        """Restituisce il grilletto destro normalizzato in [0.0, 1.0]."""
        if not self.get_state(player_index):
            return 0.0
        raw = self._state.Gamepad.bRightTrigger
        val = raw / 255.0
        return val

    def is_button_pressed(self, player_index: int = 0, button_mask: int = XINPUT_GAMEPAD_A) -> bool:
        """Restituisce True se il pulsante specificato e' premuto."""
        if not self.get_state(player_index):
            return False
        return (self._state.Gamepad.wButtons & button_mask) != 0

    def is_connected(self, player_index: int = 0) -> bool:
        if not self._dll:
            return False
        return self._dll.XInputGetState(player_index, ctypes.byref(self._state)) == 0
