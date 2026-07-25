import { IsNumber } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/** UC-18/NFR-18 · Setear un rango (min/max). La validación de plausibilidad la hace el Manager. */
export class SetRangeDto {
  @ApiProperty({ example: 90 })
  @IsNumber()
  min!: number;

  @ApiProperty({ example: 140 })
  @IsNumber()
  max!: number;
}
