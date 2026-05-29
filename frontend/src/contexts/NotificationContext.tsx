import { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import { apiNotifications } from "../api";
import type { NotificationItem } from "../types";

interface NotificationContextValue {
  notifications: NotificationItem[];
  unreadCount: number;
  loading: boolean;
  refresh: () => Promise<void>;
  markRead: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
  remove: (id: string) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextValue | null>(null);

export function useNotifications() {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error("useNotifications must be used within NotificationProvider");
  return ctx;
}

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchUnread = useCallback(async () => {
    try {
      const data = await apiNotifications.unreadCount();
      setUnreadCount(data.unread_count);
    } catch {
      // silent fail for polling
    }
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiNotifications.list(20, 0);
      setNotifications(data.items);
      setUnreadCount(data.unread_count);
    } catch (err) {
      console.error("Failed to load notifications", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const markRead = useCallback(async (id: string) => {
    try {
      await apiNotifications.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.notification_id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch (err) {
      console.error("Failed to mark read", err);
    }
  }, []);

  const markAllRead = useCallback(async () => {
    try {
      await apiNotifications.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error("Failed to mark all read", err);
    }
  }, []);

  const remove = useCallback(async (id: string) => {
    try {
      await apiNotifications.delete(id);
      const removed = notifications.find((n) => n.notification_id === id);
      setNotifications((prev) => prev.filter((n) => n.notification_id !== id));
      if (removed && !removed.is_read) {
        setUnreadCount((c) => Math.max(0, c - 1));
      }
    } catch (err) {
      console.error("Failed to delete notification", err);
    }
  }, [notifications]);

  useEffect(() => {
    refresh();
    intervalRef.current = setInterval(fetchUnread, 30000); // poll every 30s
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [refresh, fetchUnread]);

  return (
    <NotificationContext.Provider
      value={{ notifications, unreadCount, loading, refresh, markRead, markAllRead, remove }}
    >
      {children}
    </NotificationContext.Provider>
  );
}
