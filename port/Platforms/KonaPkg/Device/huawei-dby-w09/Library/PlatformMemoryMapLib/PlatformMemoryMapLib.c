#include <Library/BaseLib.h>
#include <Library/PlatformMemoryMapLib.h>
#include "MemoryMap.h"

// UNVERIFIED: candidate map from DBY-W09 XBL, DTB and Linux iomem.
// Do not build/flash firmware using this map without hardware validation.
// DT reserves 0x80000000-0x805FFFFF for HYP; skip overlapping IPC SHM.
#define DBY_REGION(name, addr, size) {name, addr, size, AddMem, SYS_MEM, SYS_MEM_CAP, Conv, WRITE_BACK_XN},

static ARM_MEMORY_REGION_DESCRIPTOR_EX gDeviceMemoryDescriptorEx[] = {
  /* XBL / uefiplat.cfg MemoryMap */
    /* OMITTED: IPC SHM 0x805D0000-0x805EFFFF overlaps HYP. */
    {"MPSS EFS          ", 0x0080600000ULL, 0x0000100000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , Reserv, WRITE_BACK_XN},
    {"BOOT INFO         ", 0x0080700000ULL, 0x0000100000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , BsData, WRITE_BACK_XN},
    {"AOP CMD DB        ", 0x0080860000ULL, 0x0000020000ULL, AddMem               , MEM_RES  , UNCACHEABLE       , Reserv, UNCACHED_UNBUFFERED_XN},
    {"XBL Log Buffer    ", 0x0080884000ULL, 0x0000010000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , Reserv, WRITE_BACK_XN},
    {"SMEM              ", 0x0080900000ULL, 0x0000200000ULL, AddMem               , MEM_RES  , UNCACHEABLE       , Reserv, UNCACHED_UNBUFFERED_XN},
    {"TZApps Reserved   ", 0x0082400000ULL, 0x0003A00000ULL, HobOnlyNoCacheSetting, MEM_RES  , UNCACHEABLE       , Reserv, UNCACHED_UNBUFFERED_XN},
    {"PIL Reserved      ", 0x0086200000ULL, 0x0005D00000ULL, AddMem               , MEM_RES  , UNCACHEABLE       , Reserv, UNCACHED_UNBUFFERED_XN},
    {"DXE Heap          ", 0x0098900000ULL, 0x0003300000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , Conv  , WRITE_BACK_XN},
    {"Sched Heap        ", 0x009BC00000ULL, 0x0000400000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , BsData, WRITE_BACK_XN},
    {"Display Reserved  ", 0x009C000000ULL, 0x0002400000ULL, AddMem               , MEM_RES  , SYS_MEM_CAP       , Reserv, WRITE_THROUGH_XN},
    {"DBI Dump          ", 0x009E400000ULL, 0x0000F00000ULL, NoHob                , MMAP_IO  , INITIALIZED       , Conv  , UNCACHED_UNBUFFERED_XN},
    {"FV Region         ", 0x009F800000ULL, 0x0000200000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , BsData, WRITE_BACK_XN},
    {"ABOOT FV          ", 0x009FA00000ULL, 0x0000200000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , Reserv, WRITE_BACK_XN},
    {"UEFI FD           ", 0x009FC00000ULL, 0x0000300000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , BsData, WRITE_BACK},
    {"SEC Heap          ", 0x009FF00000ULL, 0x000008C000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , BsData, WRITE_BACK_XN},
    {"CPU Vectors       ", 0x009FF8C000ULL, 0x0000001000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , BsData, WRITE_BACK},
    {"MMU PageTables    ", 0x009FF8D000ULL, 0x0000003000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , BsData, WRITE_BACK_XN},
    {"UEFI Stack        ", 0x009FF90000ULL, 0x0000040000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , BsData, WRITE_BACK_XN},
    {"Log Buffer        ", 0x009FFF7000ULL, 0x0000008000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , RtData, WRITE_BACK_XN},
    {"Info Blk          ", 0x009FFFF000ULL, 0x0000001000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , RtData, WRITE_BACK_XN},
    {"Kernel            ", 0x00A0000000ULL, 0x0010000000ULL, AddMem               , SYS_MEM  , SYS_MEM_CAP       , Reserv, WRITE_BACK_XN},
    {"HW Reserved       ", 0x00B0000000ULL, 0x0000401000ULL, AddMem               , MEM_RES  , UNCACHEABLE       , Reserv, UNCACHED_UNBUFFERED_XN},

  /* Secure no-map holes */
    {"QTEE NoMap", 0x80B00000ULL, 0x01900000ULL, NoHob, MEM_RES, UNCACHEABLE, Reserv, NS_DEVICE},
    {"CDSP Secure", 0x8BF00000ULL, 0x04600000ULL, NoHob, MEM_RES, UNCACHEABLE, Reserv, NS_DEVICE},

  /* Unverified conventional RAM candidates */
    DBY_CONVENTIONAL_REGION_LIST(DBY_REGION)

  /* MMIO from XBL */
    {"IMEM Base         ", 0x0014680000ULL, 0x0000040000ULL, NoHob                , MMAP_IO  , INITIALIZED       , Conv  , NS_DEVICE},
    {"IMEM Cookie Base  ", 0x00146BF000ULL, 0x0000001000ULL, AddDev               , MMAP_IO  , INITIALIZED       , Conv  , NS_DEVICE},
    {"IPC_ROUTER_TOP    ", 0x0000400000ULL, 0x0000100000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"SECURITY CONTROL  ", 0x0000780000ULL, 0x0000007000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"QUPV3_2_GSI       ", 0x0000800000ULL, 0x00000D0000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"QUPV3_0_GSI       ", 0x0000900000ULL, 0x00000D0000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"QUPV3_1_GSI       ", 0x0000A00000ULL, 0x00000D0000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"PRNG_CFG_PRNG     ", 0x0000790000ULL, 0x0000010000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"CRYPTO0 CRYPTO    ", 0x0001DC0000ULL, 0x0000040000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"TCSR_TCSR_REGS    ", 0x0001FC0000ULL, 0x0000030000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"GPU_GMU_CX_BLK    ", 0x0002C7D000ULL, 0x0000002000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"GPU_CC            ", 0x0002C90000ULL, 0x000000A000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"QUPV3_SSC_GSI     ", 0x0005A00000ULL, 0x00000D0000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"PERIPH_SS         ", 0x0008800000ULL, 0x0000200000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"MCCC_MCCC_MSTR    ", 0x00090BA000ULL, 0x0000006000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"USB30_PRIM        ", 0x000A600000ULL, 0x000011B000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"USB_RUMI          ", 0x000A720000ULL, 0x0000010000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"USB30_SEC         ", 0x000A800000ULL, 0x000011B000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"AOSS              ", 0x000B000000ULL, 0x0004000000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"TLMM_WEST         ", 0x000F100000ULL, 0x0000300000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"TLMM_SOUTH        ", 0x000F500000ULL, 0x0000300000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"TLMM_NORTH        ", 0x000F900000ULL, 0x0000300000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"SMMU              ", 0x0015000000ULL, 0x00000D0000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"APSS_HM           ", 0x0017800000ULL, 0x000D981000ULL, AddDev               , MMAP_IO  , UNCACHEABLE       , MmIO  , NS_DEVICE},
    {"Terminator", 0, 0, 0, 0, 0, 0, 0}
};

ARM_MEMORY_REGION_DESCRIPTOR_EX *GetPlatformMemoryMap(void)
{
    return gDeviceMemoryDescriptorEx;
}
