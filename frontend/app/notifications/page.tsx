import { getNotificationSubscribers, getNotifications } from "@/lib/api";
import {
  deliveryStatusLabel,
  notificationChannelLabel,
  notificationTypeLabel,
} from "@/lib/labels";

import { EmailSubscriberManager } from "@/components/EmailSubscriberManager";

export const dynamic = "force-dynamic";

export default async function NotificationsPage() {
  const [notifications, subscribers] = await Promise.all([
    getNotifications(),
    getNotificationSubscribers(),
  ]);

  return (
    <section>
      <header className="page-header">
        <h2>Bildirimler</h2>
        <p>Eşleşme bildirimi e-posta adresleri ve gönderim kayıtları.</p>
      </header>

      <EmailSubscriberManager initialSubscribers={subscribers} />

      <h3 style={{ marginTop: "1.5rem", marginBottom: "0.5rem", fontSize: "1rem", fontWeight: 600 }}>Bildirim Kayıtları</h3>
      <p className="text-muted" style={{ marginBottom: "0.75rem" }}>Gönderilen, bekleyen ve hatalı bildirim kayıtları.</p>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>İhale</th>
              <th>Kanal</th>
              <th>Alıcı</th>
              <th>Tip</th>
              <th>Durum</th>
              <th>Tarih</th>
              <th>Hata</th>
            </tr>
          </thead>
          <tbody>
            {notifications.map((record) => (
                <tr key={record.id}>
                  <td>{record.id}</td>
                  <td>{record.tender_id || "-"}</td>
                  <td>{notificationChannelLabel(record.channel)}</td>
                  <td>{record.recipient}</td>
                  <td>{notificationTypeLabel(record.notification_type)}</td>
                  <td>{deliveryStatusLabel(record.delivery_status)}</td>
                  <td>{new Date(record.created_at).toLocaleString("tr-TR")}</td>
                  <td>{record.error_message || "-"}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
