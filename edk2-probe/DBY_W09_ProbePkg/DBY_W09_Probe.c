/** DBY-W09 EDK2 ARM64 compile probe.
 * UEFI application only: NOT firmware, BootShim, or an Android image.
 * SPDX-License-Identifier: BSD-2-Clause-Patent
 */
#include <Uefi.h>
#include <Library/UefiApplicationEntryPoint.h>
EFI_STATUS
EFIAPI
UefiMain (
  IN EFI_HANDLE ImageHandle,
  IN EFI_SYSTEM_TABLE *SystemTable
  )
{
  EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *Console;
  (VOID)ImageHandle;
  if ((SystemTable == NULL) || (SystemTable->ConOut == NULL)) {
    return EFI_NOT_READY;
  }
  Console = SystemTable->ConOut;
  return Console->OutputString(
    Console,
    L"DBY-W09 EDK2 AARCH64 compile probe (NOT device firmware)\r\n"
  );
}
