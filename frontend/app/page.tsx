'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  FormControl,
  Grid,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography
} from '@mui/material';

import {
  BreakEvenResponse,
  PricePattern,
  PriceSimulationResponse,
  calculatePriceSimulation,
  getBreakEven
} from '../lib/api';

const DEFAULT_MARGIN_RATES = [0.1, 0.15, 0.2, 0.25, 0.3];

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY', maximumFractionDigits: 0 }).format(
    value
  );
}

function formatPercent(rate: number): string {
  return `${(rate * 100).toFixed(1)}%`;
}

export default function HomePage() {
  const [productName, setProductName] = useState('');
  const [unitCost, setUnitCost] = useState<number>(620);
  const [targetMargin, setTargetMargin] = useState<number>(0.2);
  const [quantity, setQuantity] = useState<number | ''>('');
  const [simulation, setSimulation] = useState<PriceSimulationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });
  const [breakEven, setBreakEven] = useState<BreakEvenResponse | null>(null);
  const [loadingBreakEven, setLoadingBreakEven] = useState(false);
  const [breakEvenError, setBreakEvenError] = useState<string | null>(null);

  const isBelowMinPrice = useMemo(() => {
    if (!simulation) return false;
    const minAllowed = simulation.guard.min_allowed_price_per_kg;
    if (!quantity) return false;
    const manualPrice = simulation.recommended_price_per_kg;
    return manualPrice < minAllowed;
  }, [simulation, quantity]);

  const loadBreakEven = useCallback(async () => {
    setLoadingBreakEven(true);
    setBreakEvenError(null);
    try {
      const data = await getBreakEven(selectedMonth);
      setBreakEven(data);
    } catch (err) {
      setBreakEvenError((err as Error).message);
    } finally {
      setLoadingBreakEven(false);
    }
  }, [selectedMonth]);

  useEffect(() => {
    loadBreakEven();
  }, [loadBreakEven]);

  const handleSimulate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await calculatePriceSimulation({
        product_name: productName || '未登録商品',
        unit_cost_per_kg: Number(unitCost),
        target_margin_rate: targetMargin,
        quantity_kg: quantity === '' ? undefined : Number(quantity)
      });
      setSimulation(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  const achievementColor = useMemo(() => {
    if (!breakEven) return 'default';
    switch (breakEven.status) {
      case 'safe':
        return 'success';
      case 'warning':
        return 'warning';
      case 'danger':
      default:
        return 'error';
    }
  }, [breakEven]);

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        価格設定支援システム
      </Typography>
      <Grid container spacing={3} alignItems="stretch">
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="価格シミュレーション" subheader="最低売価を下回ると保存不可" />
            <CardContent>
              <Stack spacing={2}>
                <TextField
                  label="商品名"
                  value={productName}
                  onChange={(event) => setProductName(event.target.value)}
                  placeholder="商品A"
                  fullWidth
                />
                <TextField
                  label="原価 (円/kg)"
                  type="number"
                  inputProps={{ min: 0, step: 1 }}
                  value={unitCost}
                  onChange={(event) => setUnitCost(Number(event.target.value))}
                  fullWidth
                />
                <FormControl fullWidth>
                  <InputLabel id="target-margin-label">目標粗利率</InputLabel>
                  <Select
                    labelId="target-margin-label"
                    value={targetMargin}
                    label="目標粗利率"
                    onChange={(event) => setTargetMargin(Number(event.target.value))}
                  >
                    {DEFAULT_MARGIN_RATES.map((rate) => (
                      <MenuItem key={rate} value={rate}>
                        {formatPercent(rate)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <TextField
                  label="数量 (kg)"
                  type="number"
                  inputProps={{ min: 0, step: 1 }}
                  value={quantity}
                  onChange={(event) => {
                    const value = event.target.value;
                    setQuantity(value === '' ? '' : Number(value));
                  }}
                  fullWidth
                />
                <Button variant="contained" onClick={handleSimulate} disabled={isLoading}>
                  計算する
                </Button>
                {isLoading && <LinearProgress />}
                {error && (
                  <Typography color="error" variant="body2">
                    {error}
                  </Typography>
                )}
                {simulation && (
                  <Box>
                    <Typography variant="h6">
                      推奨売価: {formatCurrency(simulation.recommended_price_per_kg)} / kg
                    </Typography>
                    <Typography variant="body1">
                      粗利益 (kgあたり): {formatCurrency(simulation.gross_profit_per_kg)}
                    </Typography>
                    {quantity !== '' && quantity !== undefined && quantity !== null && (
                      <Typography variant="body1">
                        総粗利: {formatCurrency(simulation.gross_profit_total)}
                      </Typography>
                    )}
                    {isBelowMinPrice && (
                      <Typography color="error" sx={{ mt: 1 }}>
                        最低売価を下回っています。保存できません。
                      </Typography>
                    )}
                    <Table size="small" sx={{ mt: 2 }}>
                      <TableHead>
                        <TableRow>
                          <TableCell>粗利率</TableCell>
                          <TableCell align="right">価格 (円/kg)</TableCell>
                          <TableCell align="right">粗利益 (円/kg)</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {simulation.price_patterns.map((pattern: PricePattern) => (
                          <TableRow key={pattern.margin_rate}>
                            <TableCell>{formatPercent(pattern.margin_rate)}</TableCell>
                            <TableCell align="right">{formatCurrency(pattern.price_per_kg)}</TableCell>
                            <TableCell align="right">{formatCurrency(pattern.profit_per_kg)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    <Button
                      variant="contained"
                      color="primary"
                      sx={{ mt: 2 }}
                      disabled={isBelowMinPrice}
                    >
                      計算結果を保存
                    </Button>
                  </Box>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardHeader
              title="分岐点ダッシュボード"
              action={
                <TextField
                  type="month"
                  size="small"
                  value={selectedMonth}
                  onChange={(event) => setSelectedMonth(event.target.value)}
                />
              }
            />
            <CardContent>
              {loadingBreakEven && <LinearProgress />}
              {breakEvenError && (
                <Typography color="error" variant="body2">
                  {breakEvenError}
                </Typography>
              )}
              {breakEven && !loadingBreakEven && (
                <Stack spacing={2}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography variant="h6">{breakEven.year_month} の状況</Typography>
                    <Chip label={breakEven.status.toUpperCase()} color={achievementColor as any} />
                  </Stack>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <InfoCard label="固定費" value={formatCurrency(breakEven.fixed_costs)} />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <InfoCard label="累計売上" value={formatCurrency(breakEven.current_revenue)} />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <InfoCard label="変動費率" value={formatPercent(breakEven.variable_cost_rate)} />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <InfoCard label="分岐点売上" value={formatCurrency(breakEven.break_even_revenue)} />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <InfoCard label="進捗率" value={formatPercent(breakEven.achievement_rate)} />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <InfoCard label="超過額/不足額" value={formatCurrency(breakEven.delta_revenue)} />
                    </Grid>
                  </Grid>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(100, breakEven.achievement_rate * 100)}
                    color={achievementColor as any}
                    sx={{ height: 12, borderRadius: 6 }}
                  />
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h6">{value}</Typography>
      </CardContent>
    </Card>
  );
}
