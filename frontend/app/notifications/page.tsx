import { getNotifications } from "@/lib/api";
import {
  deliveryStatusLabel,
  notificationChannelLabel,
  notificationTypeLabel,
} from "@/lib/labels";

export const dynamic = "force-dynamic";

export default async function NotificationsPage() {
  const notifications = await getNotifications();

  return (
    <section>
      <header className="page-header">
        <h2>Bildirim Kayıtları</h2>
        <p>Gönderilen, bekleyen ve hatalı bildirim kayıtları.</p>
      </header>

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
