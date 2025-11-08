import type { Metadata } from 'next';
import ThemeRegistry from '../components/ThemeRegistry';
import './globals.css';

export const metadata: Metadata = {
  title: 'Pricing Decision Support System',
  description: '卸売業向けのリアルタイム価格設定支援ツール'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <ThemeRegistry>
          <main>{children}</main>
        </ThemeRegistry>
      </body>
    </html>
  );
}
